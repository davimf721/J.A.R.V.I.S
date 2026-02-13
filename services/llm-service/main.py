"""
LLM Service - Microserviço para integração com LLMs
Suporta: Groq (recomendado), Ollama (local)
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import sys
import os
import time
from datetime import datetime

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.config import (
    LLM_PROVIDER, 
    GROQ_API_KEY, GROQ_MODEL,
    OLLAMA_URL, OLLAMA_MODEL, 
    LLM_TIMEOUT
)
from shared.utils import get_logger, cache

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS LLM Service",
    description="Serviço de geração de texto via Groq/Ollama",
    version="2.0.0"
)

logger = get_logger(__name__)

# Inicializar cliente Groq se disponível
groq_client = None
if LLM_PROVIDER == "groq" and GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info(f"✅ Groq configurado com modelo {GROQ_MODEL}")
    except ImportError:
        logger.warning("⚠️ Biblioteca groq não instalada, usando Ollama")


# ==================== MODELS ====================
class GenerateRequest(BaseModel):
    """Requisição para gerar texto"""
    prompt: str
    context: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    user_id: str = ""


class GenerateResponse(BaseModel):
    """Resposta da geração"""
    text: str
    model: str
    generated_tokens: int
    execution_time_seconds: float
    provider: str = "groq"


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    provider = LLM_PROVIDER
    available = False
    model = ""
    
    if provider == "groq" and groq_client:
        available = bool(GROQ_API_KEY)
        model = GROQ_MODEL
    else:
        available = await check_ollama_available()
        model = OLLAMA_MODEL
        provider = "ollama"
    
    return {
        "status": "healthy" if available else "degraded",
        "service": "llm-service",
        "provider": provider,
        "model": model,
        "llm_available": available,
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== HELPER FUNCTIONS ====================
async def check_ollama_available() -> bool:
    """Verifica se Ollama está disponível"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://ollama:11435/api/tags")
            return response.status_code == 200
    except:
        return False


async def generate_with_groq(prompt: str, temperature: float, max_tokens: int) -> dict:
    """Gera texto usando Groq API (rápido e gratuito)"""
    if not groq_client:
        raise HTTPException(status_code=503, detail="Groq não configurado. Defina GROQ_API_KEY")
    
    start_time = time.time()
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em criar conteúdo para podcasts em português brasileiro. Seja criativo, envolvente e informativo."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=GROQ_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        text = chat_completion.choices[0].message.content
        tokens = chat_completion.usage.completion_tokens if chat_completion.usage else len(text.split())
        
        return {
            "text": text,
            "model": GROQ_MODEL,
            "generated_tokens": tokens,
            "execution_time_seconds": time.time() - start_time,
            "provider": "groq"
        }
    except Exception as e:
        logger.error(f"❌ Erro Groq: {e}")
        raise HTTPException(status_code=503, detail=f"Erro Groq: {str(e)}")


async def generate_with_ollama(prompt: str, temperature: float, max_tokens: int) -> dict:
    """Gera texto usando Ollama (local)"""
    if not await check_ollama_available():
        raise HTTPException(status_code=503, detail="Ollama não está disponível")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            }
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=503, detail=f"Ollama erro: {response.status_code}")
    
    data = response.json()
    text = data.get("response", "")
    
    return {
        "text": text,
        "model": OLLAMA_MODEL,
        "generated_tokens": len(text.split()),
        "execution_time_seconds": time.time() - start_time,
        "provider": "ollama"
    }


# ==================== ENDPOINTS ====================
@app.post("/api/llm/generate")
async def generate_text(request: GenerateRequest) -> GenerateResponse:
    """
    Gera texto usando Groq (preferido) ou Ollama (fallback)
    """
    try:
        # Determinar provedor
        use_groq = LLM_PROVIDER == "groq" and groq_client is not None
        provider_name = "Groq" if use_groq else "Ollama"
        model_name = GROQ_MODEL if use_groq else OLLAMA_MODEL
        
        logger.info(f"🤖 Gerando texto com {provider_name} ({model_name})...")
        
        # Verificar cache
        cache_key = f"llm:prompt:{hash(request.prompt + request.context)}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("📦 Resposta retornada do cache")
            return GenerateResponse(**cached)
        
        # Preparar prompt com contexto
        full_prompt = request.prompt
        if request.context:
            full_prompt = f"{request.context}\n\n{request.prompt}"
        
        # Gerar com o provedor apropriado
        if use_groq:
            result = await generate_with_groq(full_prompt, request.temperature, request.max_tokens)
        else:
            result = await generate_with_ollama(full_prompt, request.temperature, request.max_tokens)
        
        logger.info(f"✅ Texto gerado ({len(result['text'])} chars em {result['execution_time_seconds']:.1f}s)")
        
        # Cachear por 1 hora
        cache.set(cache_key, result, expire_seconds=3600)
        
        return GenerateResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar texto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/llm/info")
async def get_llm_info():
    """Retorna informações sobre o LLM configurado"""
    return {
        "provider": LLM_PROVIDER,
        "model": GROQ_MODEL if LLM_PROVIDER == "groq" else OLLAMA_MODEL,
        "groq_configured": bool(GROQ_API_KEY),
        "ollama_available": await check_ollama_available(),
        "supported_providers": ["groq", "ollama"]
    }


@app.post("/api/llm/stream")
async def stream_text(request: GenerateRequest):
    """
    Gera texto em streaming (para respostas longas)
    """
    raise HTTPException(
        status_code=501,
        detail="Streaming ainda não implementado - use /api/llm/generate"
    )


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

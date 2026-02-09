"""
LLM Service - Microserviço para integração com Ollama
Fornece endpoints para gerar conteúdo via LLM
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import logging
import sys
import os
from datetime import datetime

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.config import OLLAMA_URL, OLLAMA_MODEL, LLM_TIMEOUT
from shared.utils import get_logger, cache

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS LLM Service",
    description="Serviço de geração de texto via Ollama",
    version="1.0.0"
)

logger = get_logger(__name__)


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


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    ollama_available = await check_ollama_available()
    
    return {
        "status": "healthy" if ollama_available else "degraded",
        "service": "llm-service",
        "ollama_model": OLLAMA_MODEL,
        "ollama_available": ollama_available,
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


# ==================== ENDPOINTS ====================
@app.post("/api/llm/generate")
async def generate_text(request: GenerateRequest) -> GenerateResponse:
    """
    Gera texto usando Ollama
    """
    try:
        logger.info(f"🤖 Gerando texto com {OLLAMA_MODEL}...")
        
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
        
        # Verificar Ollama
        if not await check_ollama_available():
            error_msg = f"""
❌ ERRO: Ollama não está disponível!

Verifique se Ollama está rodando:
- Host: ollama
- Port: 11435
- Modelo: {OLLAMA_MODEL}

Para iniciar localmente:
    $env:OLLAMA_HOST="127.0.0.1:11435" ; ollama serve
            """
            logger.error(error_msg)
            raise HTTPException(status_code=503, detail=error_msg)
        
        # Chamar Ollama
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": request.temperature
                }
            )
        
        execution_time = time.time() - start_time
        
        if response.status_code != 200:
            error_msg = f"Ollama retornou status {response.status_code}"
            logger.error(error_msg)
            raise HTTPException(status_code=503, detail=error_msg)
        
        data = response.json()
        text = data.get("response", "")
        
        logger.info(f"✅ Texto gerado ({len(text)} chars em {execution_time:.1f}s)")
        
        result = {
            "text": text,
            "model": OLLAMA_MODEL,
            "generated_tokens": len(text.split()),
            "execution_time_seconds": execution_time
        }
        
        # Cachear por 1 hora
        cache.set(cache_key, result, expire_seconds=3600)
        
        return GenerateResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao gerar texto: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/llm/stream")
async def stream_text(request: GenerateRequest):
    """
    Gera texto em streaming (para respostas longas)
    """
    # Para futuro - implementar com Server-Sent Events
    raise HTTPException(
        status_code=501,
        detail="Streaming ainda não implementado"
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

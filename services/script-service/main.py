"""
Script Service - Microserviço para geração de roteiros de podcast
Integra com LLM Service para gerar conteúdo
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime
import logging
from locale import setlocale, LC_ALL

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, ServiceClient, cache
from shared.config import SERVICE_URLS
from shared.models import AgentType

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS Script Service",
    description="Serviço de geração de roteiros de podcast",
    version="1.0.0"
)

logger = get_logger(__name__)
llm_client = ServiceClient(SERVICE_URLS["llm_service"])


# ==================== MODELS ====================
class ScriptRequest(BaseModel):
    """Requisição para gerar roteiro"""
    agent_name: str
    agent_type: str
    news: List[dict]
    memory_context: str = ""
    language: str = "pt-BR"
    podcast_duration_minutes: int = 8


class ScriptResponse(BaseModel):
    """Resposta com roteiro gerado"""
    script: str
    word_count: int
    estimated_duration_seconds: float
    agent_name: str
    language: str


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    return {
        "status": "healthy",
        "service": "script-service",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== HELPER FUNCTIONS ====================
def get_current_date_info(language: str = "pt-BR") -> tuple:
    """Retorna data e dia da semana em formato apropriado"""
    from datetime import datetime
    
    now = datetime.now()
    
    if language == "pt-BR":
        # Configurar locale para português
        try:
            setlocale(LC_ALL, 'pt_BR.UTF-8')
        except:
            pass
        
        weekday_names = [
            "segunda-feira", "terça-feira", "quarta-feira",
            "quinta-feira", "sexta-feira", "sábado", "domingo"
        ]
        
        day_name = weekday_names[now.weekday()]
        date_str = now.strftime("%d/%m/%Y")
        return day_name, date_str
    else:
        weekday_names = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday"
        ]
        day_name = weekday_names[now.weekday()]
        date_str = now.strftime("%m/%d/%Y")
        return day_name, date_str


def format_news_for_prompt(news_list: List[dict]) -> str:
    """Formata notícias para inclusão no prompt"""
    if not news_list:
        return "Nenhuma notícia disponível."
    
    formatted = "NOTÍCIAS DO DIA:\n\n"
    for i, news in enumerate(news_list, 1):
        title = news.get("title", "")
        summary = news.get("summary", "")
        source = news.get("source", "")
        
        formatted += f"{i}. {title}\n"
        formatted += f"   Resumo: {summary}\n"
        formatted += f"   Fonte: {source}\n\n"
    
    return formatted


# ==================== ENDPOINTS ====================
@app.post("/api/script/generate")
async def generate_script(request: ScriptRequest) -> ScriptResponse:
    """
    Gera roteiro de podcast baseado em notícias
    """
    try:
        logger.info(f"📝 Gerando roteiro para: {request.agent_name}")
        
        # Verificar cache
        cache_key = f"script:{request.agent_name}:{hash(str(request.news))}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("📦 Roteiro retornado do cache")
            return ScriptResponse(**cached)
        
        # Obter data e dia
        day_name, date_str = get_current_date_info(request.language)
        
        # Formatar notícias
        news_formatted = format_news_for_prompt(request.news)
        
        # Construir prompt
        memory_section = ""
        if request.memory_context:
            memory_section = f"\n\nCONTEXTO DE MEMÓRIA ANTERIOR:\n{request.memory_context}\n"
        
        prompt = f"""
Você é o J.A.R.V.I.S, um agente de IA especializado em criar podcasts diários sobre tecnologia.

Informações atuais:
- Agente: {request.agent_name}
- Data: {date_str}
- Dia: {day_name}
- Duração esperada: ~{request.podcast_duration_minutes} minutos

{news_formatted}{memory_section}

Crie um roteiro engajante de podcast sobre tecnologia que:
1. Comece com uma saudação casual e mencione o dia da semana e data
2. Selecione as 3-4 notícias mais importantes e interessantes
3. Explique cada notícia de forma clara e envolvente
4. Faça conexões entre as notícias quando possível
5. Termine com uma reflexão sobre o futuro da tecnologia

O roteiro deve ser lido em aproximadamente {request.podcast_duration_minutes} minutos (falada naturalmente).
Use linguagem conversacional e amigável.
Formato: Apenas o texto do roteiro, sem marcações.

Comece direto com o conteúdo do podcast.
"""

        # Chamar LLM Service
        llm_response = await llm_client.post(
            "/api/llm/generate",
            data={
                "prompt": prompt,
                "context": f"Agent: {request.agent_name}, Type: podcast",
                "temperature": 0.8,
                "max_tokens": 3000
            }
        )
        
        if not llm_response:
            raise Exception("LLM Service indisponível")
        
        script = llm_response.get("text", "")
        
        if not script:
            raise Exception("LLM não retornou um script válido")
        
        # Calcular estatísticas
        word_count = len(script.split())
        # Estimativa: ~130 palavras por minuto em português
        estimated_duration = (word_count / 130) * 60  # em segundos
        
        logger.info(f"✅ Roteiro gerado ({word_count} palavras, ~{estimated_duration/60:.1f} minutos)")
        
        result = {
            "script": script,
            "word_count": word_count,
            "estimated_duration_seconds": estimated_duration,
            "agent_name": request.agent_name,
            "language": request.language
        }
        
        # Cachear por 24 horas
        cache.set(cache_key, result, expire_seconds=86400)
        
        return ScriptResponse(**result)
    
    except Exception as e:
        logger.error(f"❌ Erro ao gerar roteiro: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/script/preview")
async def preview_script(agent_name: str, language: str = "pt-BR"):
    """
    Retorna um exemplo de roteiro gerado
    Útil para debug e visualização
    """
    day_name, date_str = get_current_date_info(language)
    
    example = f"""
E aí, pessoal! {day_name.capitalize()}, {date_str}.

Aqui é o {agent_name}, seu assistente de IA preferido! Hoje temos notícias incríveis do mundo da tecnologia.

Primeiro assunto: Uma descoberta revolucionária em inteligência artificial que está mudando o mundo.
Este avanço promete transformar como trabalhamos e nos relacionamos com a tecnologia.

Segundo assunto: Novos desenvolvimentos em hardware que prometem melhorar a performance dos seus dispositivos.
As últimas inovações estão tornando nossos computadores mais rápidos e eficientes.

Terceiro assunto: Atualizações importantes em segurança cibernética que você precisa saber.
Especialistas alertam para novas ameaças e as melhores práticas para se proteger.

Nesses tempos incríveis de transformação tecnológica, uma coisa é certa:
o futuro está sendo construído agora, e você pode fazer parte dessa revolução!

Obrigado por ouvir o podcast de hoje. Nos vemos amanhã!
"""
    
    return {
        "preview": example,
        "word_count": len(example.split()),
        "estimated_duration_seconds": (len(example.split()) / 130) * 60
    }


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )

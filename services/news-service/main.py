"""
News Service - Microserviço para busca e processamento de notícias
Reutiliza o código de news_fetcher.py existente
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime
import logging

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, cache
from shared.models import NewsItem

# Importar o news fetcher existente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../jarvis-core'))
try:
    from tools.news_fetcher import fetch_news_parallel
except ImportError:
    fetch_news_parallel = None

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS News Service",
    description="Serviço de busca e processamento de notícias",
    version="1.0.0"
)

logger = get_logger(__name__)


# ==================== MODELS ====================
class NewsRequest(BaseModel):
    """Requisição para buscar notícias"""
    language: str = "pt-BR"
    limit: int = 8
    categories: Optional[List[str]] = None
    skip_cache: bool = False


class NewsResponse(BaseModel):
    """Resposta com notícias"""
    news: List[dict]
    total_count: int
    language: str
    source_count: int
    cached: bool


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    return {
        "status": "healthy",
        "service": "news-service",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_available": cache.enabled
    }


# ==================== ENDPOINTS ====================
@app.post("/api/news/fetch")
async def fetch_news(request: NewsRequest) -> NewsResponse:
    """
    Busca notícias de múltiplas fontes
    """
    try:
        logger.info(f"📰 Buscando notícias ({request.language}, limit={request.limit})...")
        
        # Verificar cache
        cache_key = f"news:{request.language}:{request.limit}"
        if not request.skip_cache:
            cached_news = cache.get(cache_key)
            if cached_news:
                logger.info("📦 Notícias retornadas do cache")
                return NewsResponse(
                    news=cached_news,
                    total_count=len(cached_news),
                    language=request.language,
                    source_count=0,
                    cached=True
                )
        
        # Buscar notícias (usando função existente)
        if fetch_news_parallel:
            news_list = fetch_news_parallel(limit=request.limit)
        else:
            logger.warning("News fetcher não disponível, retornando lista vazia")
            news_list = []
        
        # Converter para dict
        news_dicts = [
            {
                "title": n.get("title", ""),
                "summary": n.get("summary", ""),
                "source": n.get("source", ""),
                "url": n.get("url", ""),
                "published_at": n.get("published_at", ""),
                "language": request.language
            }
            for n in news_list
        ]
        
        logger.info(f"✅ {len(news_dicts)} notícias encontradas")
        
        # Cachear por 4 horas
        cache.set(cache_key, news_dicts, expire_seconds=14400)
        
        return NewsResponse(
            news=news_dicts,
            total_count=len(news_dicts),
            language=request.language,
            source_count=len(set(n["source"] for n in news_dicts)),
            cached=False
        )
    
    except Exception as e:
        logger.error(f"❌ Erro ao buscar notícias: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/news/sources")
async def get_sources():
    """Lista as fontes de notícias disponíveis"""
    sources = [
        {"name": "DioLinux", "language": "pt-BR"},
        {"name": "Infowester", "language": "pt-BR"},
        {"name": "ArsTechnica", "language": "en-US"},
        {"name": "The Verge", "language": "en-US"},
        {"name": "Hacker News", "language": "en-US"},
        {"name": "TechCrunch", "language": "en-US"},
        {"name": "Dev.to", "language": "en-US"},
    ]
    return {"sources": sources, "total": len(sources)}


@app.post("/api/news/clear-cache")
async def clear_cache():
    """Limpa o cache de notícias"""
    count = cache.clear_pattern("news:*")
    logger.info(f"🗑️  Cache limpo: {count} chaves removidas")
    return {"cleared": count}


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )

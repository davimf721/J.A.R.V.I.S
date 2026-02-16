"""
News Service - Microserviço para busca e processamento de notícias
Busca notícias de feeds RSS de sites de tecnologia
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from datetime import datetime
import logging
import feedparser
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, cache
from shared.models import NewsItem

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS News Service",
    description="Serviço de busca e processamento de notícias",
    version="1.0.0"
)

logger = get_logger(__name__)

# ==================== RSS FEEDS ====================
# Feeds gerais de tecnologia
RSS_FEEDS = {
    "pt-BR": [
        {"name": "Tecnoblog", "url": "https://tecnoblog.net/feed/"},
        {"name": "Olhar Digital", "url": "https://olhardigital.com.br/feed/"},
        {"name": "Canaltech", "url": "https://canaltech.com.br/rss/"},
        {"name": "TecMundo", "url": "https://rss.tecmundo.com.br/feed"},
        {"name": "Gizmodo Brasil", "url": "https://gizmodo.uol.com.br/feed/"},
    ],
    "en-US": [
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage"},
        {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    ]
}

# Feeds específicos por tipo de podcast
FEEDS_BY_TYPE = {
    "podcast_daily": {
        "pt-BR": [
            {"name": "Tecnoblog", "url": "https://tecnoblog.net/feed/"},
            {"name": "Olhar Digital", "url": "https://olhardigital.com.br/feed/"},
            {"name": "Canaltech", "url": "https://canaltech.com.br/rss/"},
            {"name": "TecMundo", "url": "https://rss.tecmundo.com.br/feed"},
            {"name": "Gizmodo Brasil", "url": "https://gizmodo.uol.com.br/feed/"},
        ],
        "en-US": [
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
            {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
        ]
    },
    "market_analysis": {
        "pt-BR": [
            {"name": "InfoMoney", "url": "https://www.infomoney.com.br/feed/"},
            {"name": "Valor Econômico Tech", "url": "https://valor.globo.com/empresas/rss"},
            {"name": "Exame Tech", "url": "https://exame.com/tecnologia/feed/"},
            {"name": "StartSe", "url": "https://www.startse.com/feed/"},
            {"name": "NeoFeed", "url": "https://neofeed.com.br/feed/"},
            {"name": "Brazil Journal", "url": "https://braziljournal.com/feed"},
        ],
        "en-US": [
            {"name": "TechCrunch Startups", "url": "https://techcrunch.com/category/startups/feed/"},
            {"name": "Bloomberg Tech", "url": "https://feeds.bloomberg.com/technology/news.rss"},
            {"name": "Reuters Tech", "url": "https://www.reutersagency.com/feed/?best-topics=tech"},
            {"name": "CNBC Tech", "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html"},
            {"name": "VentureBeat", "url": "https://venturebeat.com/feed/"},
            {"name": "Crunchbase News", "url": "https://news.crunchbase.com/feed/"},
        ]
    },
    "content_generator": {
        "pt-BR": [
            {"name": "Tecnoblog", "url": "https://tecnoblog.net/feed/"},
            {"name": "Olhar Digital", "url": "https://olhardigital.com.br/feed/"},
            {"name": "Canaltech", "url": "https://canaltech.com.br/rss/"},
            {"name": "MIT Technology Review Brasil", "url": "https://mittechreview.com.br/feed/"},
        ],
        "en-US": [
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
            {"name": "IEEE Spectrum", "url": "https://spectrum.ieee.org/feeds/feed.rss"},
            {"name": "Quanta Magazine", "url": "https://www.quantamagazine.org/feed/"},
        ]
    },
    "code_assistant": {
        "pt-BR": [
            {"name": "iMasters", "url": "https://imasters.com.br/feed"},
            {"name": "TabNews", "url": "https://www.tabnews.com.br/recentes/rss"},
            {"name": "Dev.to Brasil", "url": "https://dev.to/feed/tag/brazil"},
            {"name": "Tecnoblog Dev", "url": "https://tecnoblog.net/categoria/dev/feed/"},
        ],
        "en-US": [
            {"name": "Hacker News", "url": "https://hnrss.org/frontpage"},
            {"name": "Dev.to", "url": "https://dev.to/feed"},
            {"name": "CSS-Tricks", "url": "https://css-tricks.com/feed/"},
            {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/"},
            {"name": "GitHub Blog", "url": "https://github.blog/feed/"},
            {"name": "The Changelog", "url": "https://changelog.com/feed"},
        ]
    },
    "email_summary": {
        "pt-BR": [
            {"name": "InfoMoney", "url": "https://www.infomoney.com.br/feed/"},
            {"name": "Tecnoblog", "url": "https://tecnoblog.net/feed/"},
            {"name": "Exame Tech", "url": "https://exame.com/tecnologia/feed/"},
        ],
        "en-US": [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "Bloomberg Tech", "url": "https://feeds.bloomberg.com/technology/news.rss"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        ]
    }
}


def fetch_from_rss(feed_info: dict, limit: int = 5) -> List[dict]:
    """Busca notícias de um feed RSS"""
    try:
        # Timeout mais curto para evitar travamentos
        import socket
        socket.setdefaulttimeout(10)
        
        feed = feedparser.parse(feed_info["url"])
        news = []
        
        if not feed.entries:
            return []
        
        for entry in feed.entries[:limit]:
            # Extrair resumo
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description
            
            # Limpar HTML do resumo
            import re
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary[:500] if len(summary) > 500 else summary
            
            # Extrair data
            published = ""
            if hasattr(entry, 'published'):
                published = entry.published
            elif hasattr(entry, 'updated'):
                published = entry.updated
            
            news.append({
                "title": entry.get("title", ""),
                "summary": summary.strip(),
                "source": feed_info["name"],
                "url": entry.get("link", ""),
                "published_at": published
            })
        
        return news
    except Exception as e:
        logger.warning(f"Erro ao buscar feed {feed_info['name']}: {e}")
        return []


def fetch_news_parallel(language: str = "pt-BR", limit: int = 10, agent_type: str = "podcast_daily") -> List[dict]:
    """Busca notícias de múltiplos feeds em paralelo baseado no tipo de agente"""
    
    # Buscar feeds específicos do tipo de agente
    type_feeds = FEEDS_BY_TYPE.get(agent_type, {})
    feeds = type_feeds.get(language, type_feeds.get("en-US", []))
    
    # Fallback para feeds gerais se não houver específicos
    if not feeds:
        feeds = RSS_FEEDS.get(language, RSS_FEEDS.get("en-US", []))
    
    logger.info(f"🎯 Buscando notícias para tipo '{agent_type}' com {len(feeds)} fontes")
    
    all_news = []
    
    if not feeds:
        return []
    
    # Calcular quantas notícias por feed
    per_feed = max(3, limit // len(feeds) + 1)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(fetch_from_rss, feed, per_feed): feed 
            for feed in feeds
        }
        
        for future in as_completed(futures, timeout=30):
            try:
                news = future.result(timeout=10)
                if news:
                    all_news.extend(news)
                    logger.info(f"✅ Obtidas {len(news)} notícias de {futures[future]['name']}")
            except Exception as e:
                feed_name = futures[future].get('name', 'unknown')
                logger.warning(f"⚠️ Timeout/erro no feed {feed_name}: {e}")
    
    # Ordenar por data (mais recentes primeiro) e limitar
    all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    
    logger.info(f"📰 Total: {len(all_news)} notícias coletadas")
    return all_news[:limit]


# ==================== MODELS ====================
class NewsRequest(BaseModel):
    """Requisição para buscar notícias"""
    language: str = "pt-BR"
    limit: int = 10
    categories: Optional[List[str]] = None
    skip_cache: bool = False
    # Tipo de agente para buscar fontes específicas
    agent_type: str = "podcast_daily"
    # Campos de preferência para personalização
    user_id: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    blocked_categories: Optional[List[str]] = None
    preferred_sources: Optional[List[str]] = None
    blocked_sources: Optional[List[str]] = None
    keywords_boost: Optional[List[str]] = None
    keywords_block: Optional[List[str]] = None


class NewsResponse(BaseModel):
    """Resposta com notícias"""
    news: List[dict]
    total_count: int
    language: str
    source_count: int
    cached: bool
    personalized: bool = False
    agent_type: str = "podcast_daily"


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
    Busca notícias de múltiplas fontes com personalização baseada em preferências
    Usa fontes específicas baseadas no tipo de agente (agent_type)
    """
    try:
        logger.info(f"📰 Buscando notícias ({request.language}, tipo={request.agent_type}, limit={request.limit})...")
        
        # Verificar cache (apenas se não houver personalização)
        is_personalized = any([
            request.preferred_categories,
            request.blocked_categories,
            request.preferred_sources,
            request.blocked_sources,
            request.keywords_boost,
            request.keywords_block
        ])
        
        cache_key = f"news:{request.agent_type}:{request.language}:{request.limit}"
        if not request.skip_cache and not is_personalized:
            cached_news = cache.get(cache_key)
            if cached_news:
                logger.info("📦 Notícias retornadas do cache")
                return NewsResponse(
                    news=cached_news,
                    total_count=len(cached_news),
                    language=request.language,
                    source_count=0,
                    cached=True,
                    personalized=False,
                    agent_type=request.agent_type
                )
        
        # Buscar notícias de feeds RSS específicos para o tipo de agente
        # Buscar mais notícias se houver filtros para aplicar
        fetch_limit = request.limit * 3 if is_personalized else request.limit
        
        news_list = fetch_news_parallel(
            language=request.language, 
            limit=fetch_limit,
            agent_type=request.agent_type
        )
        
        # Converter para dict com categoria detectada
        news_dicts = [
            {
                "title": n.get("title", ""),
                "summary": n.get("summary", ""),
                "source": n.get("source", ""),
                "url": n.get("url", ""),
                "published_at": n.get("published_at", ""),
                "language": request.language,
                "category": _detect_category(n.get("title", "") + " " + n.get("summary", ""))
            }
            for n in news_list
        ]
        
        # Aplicar personalização se houver preferências
        if is_personalized:
            news_dicts = _apply_preferences(
                news_dicts,
                preferred_categories=request.preferred_categories,
                blocked_categories=request.blocked_categories,
                preferred_sources=request.preferred_sources,
                blocked_sources=request.blocked_sources,
                keywords_boost=request.keywords_boost,
                keywords_block=request.keywords_block
            )
            logger.info(f"🎯 Notícias personalizadas: {len(news_dicts)} após filtros")
        
        # Limitar ao número solicitado
        news_dicts = news_dicts[:request.limit]
        
        logger.info(f"✅ {len(news_dicts)} notícias encontradas")
        
        # Cachear apenas notícias não personalizadas por 4 horas
        if not is_personalized:
            cache.set(cache_key, news_dicts, expire_seconds=14400)
        
        return NewsResponse(
            news=news_dicts,
            total_count=len(news_dicts),
            language=request.language,
            source_count=len(set(n["source"] for n in news_dicts)),
            cached=False,
            personalized=is_personalized
        )
    
    except Exception as e:
        logger.error(f"❌ Erro ao buscar notícias: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _detect_category(text: str) -> str:
    """
    Detecta categoria da notícia baseado no texto
    """
    text_lower = text.lower()
    
    categories = {
        "ai": ["inteligência artificial", "ia", "machine learning", "deep learning", "gpt", "llm", "openai", "chatgpt", "ai", "neural"],
        "programming": ["programação", "código", "python", "javascript", "rust", "golang", "developer", "programming", "code"],
        "cloud": ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "devops", "nuvem"],
        "security": ["segurança", "hacker", "cibersegurança", "vulnerability", "security", "breach", "malware"],
        "mobile": ["android", "ios", "apple", "google", "smartphone", "app", "mobile"],
        "hardware": ["processador", "gpu", "nvidia", "amd", "intel", "hardware", "chip"],
        "gaming": ["game", "gaming", "jogos", "playstation", "xbox", "nintendo", "steam"],
        "business": ["startup", "empresa", "mercado", "investimento", "business", "funding"],
        "linux": ["linux", "ubuntu", "debian", "fedora", "open source", "código aberto"],
        "web": ["web", "browser", "chrome", "firefox", "frontend", "backend", "api"]
    }
    
    for category, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            return category
    
    return "general"


def _apply_preferences(
    news_list: List[dict],
    preferred_categories: Optional[List[str]] = None,
    blocked_categories: Optional[List[str]] = None,
    preferred_sources: Optional[List[str]] = None,
    blocked_sources: Optional[List[str]] = None,
    keywords_boost: Optional[List[str]] = None,
    keywords_block: Optional[List[str]] = None
) -> List[dict]:
    """
    Aplica preferências do usuário para filtrar e ordenar notícias
    """
    filtered_news = []
    
    for news in news_list:
        title_summary = (news.get("title", "") + " " + news.get("summary", "")).lower()
        source = news.get("source", "").lower()
        category = news.get("category", "general").lower()
        
        # Verificar bloqueios (remover notícia se bloqueada)
        if blocked_categories and category in [c.lower() for c in blocked_categories]:
            continue
        
        if blocked_sources and source in [s.lower() for s in blocked_sources]:
            continue
        
        if keywords_block:
            if any(kw.lower() in title_summary for kw in keywords_block):
                continue
        
        # Calcular score de relevância
        score = 0
        
        # Boost por categoria preferida
        if preferred_categories and category in [c.lower() for c in preferred_categories]:
            score += 10
        
        # Boost por fonte preferida
        if preferred_sources and source in [s.lower() for s in preferred_sources]:
            score += 5
        
        # Boost por palavras-chave
        if keywords_boost:
            for kw in keywords_boost:
                if kw.lower() in title_summary:
                    score += 3
        
        # Adicionar score ao news
        news["_preference_score"] = score
        filtered_news.append(news)
    
    # Ordenar por score de preferência (maior primeiro)
    filtered_news.sort(key=lambda x: x.get("_preference_score", 0), reverse=True)
    
    # Remover score interno antes de retornar
    for news in filtered_news:
        news.pop("_preference_score", None)
    
    return filtered_news


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

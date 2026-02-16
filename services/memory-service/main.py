"""
Memory Service - Microserviço para gerenciamento de memória vetorial
Integra com ChromaDB para armazenamento semântico
Inclui sistema de aprendizado de preferências do usuário
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
import os
from datetime import datetime
import logging
import json

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, cache
from shared.config import CHROMADB_HOST, CHROMADB_PORT, CHROMADB_PERSIST_DIR

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS Memory Service",
    description="Serviço de memória vetorial com ChromaDB",
    version="1.0.0"
)

logger = get_logger(__name__)

# Inicializar ChromaDB
try:
    import chromadb
    
    # Usando cliente HTTP para conectar ao container ChromaDB
    chroma_client = chromadb.HttpClient(
        host=CHROMADB_HOST,
        port=int(CHROMADB_PORT)
    )
    # Testar conexão
    chroma_client.heartbeat()
    logger.info(f"✅ ChromaDB conectado em {CHROMADB_HOST}:{CHROMADB_PORT}")
except Exception as e:
    logger.error(f"❌ Erro ao conectar ChromaDB: {e}")
    chroma_client = None


# ==================== MODELS ====================
class MemoryStoreRequest(BaseModel):
    """Requisição para armazenar memória"""
    user_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    category: str = "default"


class MemoryRecallRequest(BaseModel):
    """Requisição para recuperar memória"""
    user_id: str
    query: str
    limit: int = 3
    threshold: float = 0.5


class MemoryResponse(BaseModel):
    """Resposta com memória"""
    id: str
    content: str
    similarity: float
    metadata: Optional[Dict] = None
    stored_at: str


# ==================== PREFERENCE MODELS ====================
class UserPreferences(BaseModel):
    """Preferências do usuário para personalização de conteúdo"""
    # Interesses (o que o usuário QUER ver mais)
    interests: List[str] = Field(default_factory=list, description="Tópicos de interesse")
    favorite_sources: List[str] = Field(default_factory=list, description="Fontes favoritas")
    
    # Bloqueios (o que o usuário NÃO quer ver)
    blocked_topics: List[str] = Field(default_factory=list, description="Tópicos bloqueados")
    blocked_sources: List[str] = Field(default_factory=list, description="Fontes bloqueadas")


class QuickFeedback(BaseModel):
    """Feedback rápido sobre o podcast"""
    user_id: str
    podcast_id: str
    # Avaliação geral do podcast (1-5)
    rating: int = Field(ge=1, le=5, description="Nota de 1 a 5")
    # Feedback específico opcional
    liked_news: List[int] = Field(default_factory=list, description="Índices das notícias que gostou (1, 2, 3...)")
    disliked_news: List[int] = Field(default_factory=list, description="Índices das notícias que não gostou")
    comment: Optional[str] = Field(None, description="Comentário opcional")


class AddInterest(BaseModel):
    """Adicionar interesse"""
    user_id: str
    topic: str = Field(..., description="Tópico de interesse (ex: 'inteligência artificial', 'python', 'startups')")


class BlockTopic(BaseModel):
    """Bloquear tópico"""
    user_id: str
    topic: str = Field(..., description="Tópico a bloquear (ex: 'política', 'futebol', 'celebridades')")


class PodcastHistory(BaseModel):
    """Histórico de podcast para feedback"""
    podcast_id: str
    news: List[dict]
    created_at: str


class SavePodcastRequest(BaseModel):
    """Request para salvar histórico do podcast"""
    podcast_id: str
    user_id: str
    news: List[dict]


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    chromadb_available = chroma_client is not None
    
    return {
        "status": "healthy" if chromadb_available else "degraded",
        "service": "memory-service",
        "chromadb_available": chromadb_available,
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== ENDPOINTS ====================
@app.post("/api/memory/store")
async def store_memory(request: MemoryStoreRequest) -> Dict:
    """
    Armazena novo item de memória no banco vetorial
    """
    try:
        if not chroma_client:
            raise Exception("ChromaDB não disponível")
        
        logger.info(f"💾 Armazenando memória para usuário: {request.user_id}")
        
        # Obter ou criar coleção do usuário
        collection = chroma_client.get_or_create_collection(
            name=f"user_{request.user_id}",
            metadata={"user_id": request.user_id}
        )
        
        # Gerar ID único
        import uuid
        memory_id = str(uuid.uuid4())
        
        # Armazenar
        collection.add(
            ids=[memory_id],
            documents=[request.content],
            metadatas=[{
                **(request.metadata or {}),
                "category": request.category,
                "stored_at": datetime.utcnow().isoformat()
            }]
        )
        
        logger.info(f"✅ Memória armazenada: {memory_id}")
        
        return {
            "id": memory_id,
            "status": "stored",
            "user_id": request.user_id
        }
    
    except Exception as e:
        logger.error(f"❌ Erro ao armazenar memória: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/recall")
async def recall_memory(request: MemoryRecallRequest) -> Dict:
    """
    Recupera memórias relevantes baseado em query semântica
    """
    try:
        if not chroma_client:
            return {"memories": []}
        
        logger.info(f"🧠 Recuperando memórias para: {request.query}")
        
        # Obter coleção do usuário
        try:
            collection = chroma_client.get_collection(name=f"user_{request.user_id}")
        except:
            logger.info(f"ℹ️  Nenhuma memória anterior para usuário: {request.user_id}")
            return {"memories": []}
        
        # Buscar similar
        results = collection.query(
            query_texts=[request.query],
            n_results=request.limit
        )
        
        if not results or not results.get("documents"):
            return {"memories": []}
        
        # Formatar resposta
        memories = []
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if "distances" in results else 0
            # Converter distância para similarity (1 - distância)
            similarity = 1 - (distance / 2) if distance else 0.5
            
            memory = {
                "id": results["ids"][0][i] if "ids" in results else f"mem_{i}",
                "content": doc,
                "similarity": similarity,
                "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
            }
            
            if similarity >= request.threshold:
                memories.append(memory)
        
        logger.info(f"✅ {len(memories)} memória(s) recuperada(s)")
        
        return {"memories": memories}
    
    except Exception as e:
        logger.error(f"❌ Erro ao recuperar memória: {e}", exc_info=True)
        return {"memories": []}


@app.delete("/api/memory/{user_id}")
async def clear_memory(user_id: str) -> Dict:
    """
    Limpa todas as memórias de um usuário
    """
    try:
        if not chroma_client:
            raise Exception("ChromaDB não disponível")
        
        logger.info(f"🗑️  Limpando memória do usuário: {user_id}")
        
        try:
            chroma_client.delete_collection(name=f"user_{user_id}")
            logger.info(f"✅ Memória do usuário limpa")
        except:
            logger.info(f"ℹ️  Nenhuma memória para limpar")
        
        return {"status": "cleared", "user_id": user_id}
    
    except Exception as e:
        logger.error(f"❌ Erro ao limpar memória: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/stats/{user_id}")
async def get_memory_stats(user_id: str) -> Dict:
    """
    Retorna estatísticas de memória do usuário
    """
    try:
        if not chroma_client:
            return {"user_id": user_id, "total_memories": 0}
        
        try:
            collection = chroma_client.get_collection(name=f"user_{user_id}")
            count = collection.count()
            
            return {
                "user_id": user_id,
                "total_memories": count,
                "status": "ok"
            }
        except:
            return {"user_id": user_id, "total_memories": 0}
    
    except Exception as e:
        logger.error(f"❌ Erro ao obter stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PREFERENCE ENDPOINTS ====================

def _get_preferences_key(user_id: str) -> str:
    """Gera chave de cache para preferências"""
    return f"user_prefs:{user_id}"


def _get_podcast_history_key(user_id: str) -> str:
    """Gera chave para histórico de podcasts"""
    return f"podcast_history:{user_id}"


@app.get("/api/interests/{user_id}")
async def get_interests(user_id: str) -> Dict:
    """
    Retorna os interesses e bloqueios do usuário de forma simples
    """
    try:
        cache_key = _get_preferences_key(user_id)
        prefs = cache.get(cache_key) or {
            "interests": [],
            "favorite_sources": [],
            "blocked_topics": [],
            "blocked_sources": []
        }
        
        return {
            "user_id": user_id,
            "interests": prefs.get("interests", []),
            "favorite_sources": prefs.get("favorite_sources", []),
            "blocked_topics": prefs.get("blocked_topics", []),
            "blocked_sources": prefs.get("blocked_sources", []),
            "total_podcasts_rated": prefs.get("total_rated", 0),
            "average_rating": prefs.get("avg_rating", 0)
        }
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interests/add")
async def add_interest(request: AddInterest) -> Dict:
    """
    Adiciona um interesse/tópico que o usuário quer ver MAIS
    
    Exemplos de tópicos:
    - "inteligência artificial", "machine learning", "IA"
    - "python", "programação", "desenvolvimento"
    - "startups", "empreendedorismo"
    - "segurança", "cibersegurança"
    - "linux", "open source"
    - "games", "jogos"
    """
    try:
        cache_key = _get_preferences_key(request.user_id)
        prefs = cache.get(cache_key) or {"interests": [], "blocked_topics": [], "favorite_sources": [], "blocked_sources": []}
        
        topic = request.topic.lower().strip()
        
        if topic not in prefs["interests"]:
            prefs["interests"].append(topic)
            # Remover de bloqueados se estava lá
            if topic in prefs.get("blocked_topics", []):
                prefs["blocked_topics"].remove(topic)
        
        cache.set(cache_key, prefs, expire_seconds=0)
        
        logger.info(f"✅ Interesse adicionado: {topic} para {request.user_id}")
        
        return {
            "status": "added",
            "topic": topic,
            "message": f"Agora você verá mais notícias sobre '{topic}'",
            "interests": prefs["interests"]
        }
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/interests/block")
async def block_topic(request: BlockTopic) -> Dict:
    """
    Bloqueia um tópico que o usuário NÃO quer ver
    
    Exemplos:
    - "política", "eleições"
    - "futebol", "esportes"
    - "celebridades", "fofoca"
    - "guerra", "violência"
    """
    try:
        cache_key = _get_preferences_key(request.user_id)
        prefs = cache.get(cache_key) or {"interests": [], "blocked_topics": [], "favorite_sources": [], "blocked_sources": []}
        
        topic = request.topic.lower().strip()
        
        if topic not in prefs.get("blocked_topics", []):
            if "blocked_topics" not in prefs:
                prefs["blocked_topics"] = []
            prefs["blocked_topics"].append(topic)
            # Remover de interesses se estava lá
            if topic in prefs.get("interests", []):
                prefs["interests"].remove(topic)
        
        cache.set(cache_key, prefs, expire_seconds=0)
        
        logger.info(f"🚫 Tópico bloqueado: {topic} para {request.user_id}")
        
        return {
            "status": "blocked",
            "topic": topic,
            "message": f"Você não verá mais notícias sobre '{topic}'",
            "blocked_topics": prefs.get("blocked_topics", [])
        }
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/interests/{user_id}/remove/{topic}")
async def remove_interest_or_block(user_id: str, topic: str) -> Dict:
    """Remove um interesse ou bloqueio"""
    try:
        cache_key = _get_preferences_key(user_id)
        prefs = cache.get(cache_key) or {"interests": [], "blocked_topics": []}
        
        topic = topic.lower().strip()
        removed_from = []
        
        if topic in prefs.get("interests", []):
            prefs["interests"].remove(topic)
            removed_from.append("interests")
        
        if topic in prefs.get("blocked_topics", []):
            prefs["blocked_topics"].remove(topic)
            removed_from.append("blocked_topics")
        
        cache.set(cache_key, prefs, expire_seconds=0)
        
        return {
            "status": "removed",
            "topic": topic,
            "removed_from": removed_from
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/podcast/save-news")
async def save_podcast_news(request: SavePodcastRequest) -> Dict:
    """
    Salva as notícias de um podcast para referência no feedback
    (Chamado automaticamente pelo orchestrator)
    """
    try:
        history_key = _get_podcast_history_key(request.user_id)
        
        # Simplificar as notícias para exibição
        simplified_news = []
        for i, n in enumerate(request.news, 1):
            simplified_news.append({
                "index": i,
                "title": n.get("title", "")[:100],
                "source": n.get("source", ""),
                "category": n.get("category", "general")
            })
        
        history = {
            "podcast_id": request.podcast_id,
            "news": simplified_news,
            "created_at": datetime.utcnow().isoformat()
        }
        
        cache.set(history_key, history, expire_seconds=86400 * 7)  # 7 dias
        
        return {"status": "saved", "podcast_id": request.podcast_id, "news_count": len(request.news)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/podcast/last/{user_id}")
async def get_last_podcast_news(user_id: str) -> Dict:
    """
    Retorna as notícias do último podcast para dar feedback
    """
    try:
        history_key = _get_podcast_history_key(user_id)
        history = cache.get(history_key)
        
        if not history:
            return {
                "user_id": user_id,
                "message": "Nenhum podcast recente encontrado",
                "news": []
            }
        
        return {
            "user_id": user_id,
            "podcast_id": history.get("podcast_id"),
            "created_at": history.get("created_at"),
            "news": history.get("news", []),
            "instructions": "Use os índices (1, 2, 3...) para dar feedback nas notícias"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/podcast/rate")
async def rate_podcast(feedback: QuickFeedback) -> Dict:
    """
    Avalia o podcast de forma rápida e simples
    
    - rating: 1-5 (nota geral)
    - liked_news: [1, 3] (índices das notícias que gostou)
    - disliked_news: [2] (índices das notícias que não gostou)
    """
    try:
        logger.info(f"⭐ Rating {feedback.rating}/5 de {feedback.user_id}")
        
        # Buscar histórico do podcast
        history_key = _get_podcast_history_key(feedback.user_id)
        history = cache.get(history_key) or {}
        news_list = history.get("news", [])
        
        # Atualizar preferências baseado no feedback
        cache_key = _get_preferences_key(feedback.user_id)
        prefs = cache.get(cache_key) or {
            "interests": [], 
            "blocked_topics": [],
            "favorite_sources": [],
            "blocked_sources": [],
            "total_rated": 0,
            "total_score": 0
        }
        
        # Atualizar média de rating
        prefs["total_rated"] = prefs.get("total_rated", 0) + 1
        prefs["total_score"] = prefs.get("total_score", 0) + feedback.rating
        prefs["avg_rating"] = prefs["total_score"] / prefs["total_rated"]
        
        learned_interests = []
        learned_blocks = []
        
        # Processar notícias que gostou
        for idx in feedback.liked_news:
            if 1 <= idx <= len(news_list):
                news = news_list[idx - 1]
                category = news.get("category", "").lower()
                source = news.get("source", "")
                
                # Adicionar categoria aos interesses
                if category and category not in prefs["interests"] and category != "general":
                    prefs["interests"].append(category)
                    learned_interests.append(category)
                
                # Adicionar fonte aos favoritos
                if source and source not in prefs.get("favorite_sources", []):
                    if "favorite_sources" not in prefs:
                        prefs["favorite_sources"] = []
                    prefs["favorite_sources"].append(source)
        
        # Processar notícias que não gostou
        for idx in feedback.disliked_news:
            if 1 <= idx <= len(news_list):
                news = news_list[idx - 1]
                category = news.get("category", "").lower()
                source = news.get("source", "")
                
                # Adicionar categoria aos bloqueados (se aparecer 2+ vezes)
                block_count_key = f"dislike_count:{feedback.user_id}:{category}"
                count = cache.get(block_count_key) or 0
                count += 1
                cache.set(block_count_key, count, expire_seconds=86400 * 30)
                
                if count >= 2 and category not in prefs.get("blocked_topics", []) and category != "general":
                    if "blocked_topics" not in prefs:
                        prefs["blocked_topics"] = []
                    prefs["blocked_topics"].append(category)
                    learned_blocks.append(category)
                    # Remover dos interesses se estava lá
                    if category in prefs["interests"]:
                        prefs["interests"].remove(category)
        
        cache.set(cache_key, prefs, expire_seconds=0)
        
        # Mensagem de retorno
        messages = [f"Obrigado! Podcast avaliado com {feedback.rating}/5 ⭐"]
        
        if learned_interests:
            messages.append(f"Aprendido: você gosta de {', '.join(learned_interests)}")
        
        if learned_blocks:
            messages.append(f"Aprendido: você não gosta de {', '.join(learned_blocks)}")
        
        if feedback.rating >= 4:
            messages.append("Que bom que gostou! 😊")
        elif feedback.rating <= 2:
            messages.append("Vamos melhorar! Adicione interesses para personalizar.")
        
        return {
            "status": "rated",
            "rating": feedback.rating,
            "learned_interests": learned_interests,
            "learned_blocks": learned_blocks,
            "messages": messages,
            "current_interests": prefs["interests"][:5],
            "podcasts_rated": prefs["total_rated"]
        }
    
    except Exception as e:
        logger.error(f"❌ Erro ao avaliar podcast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Manter compatibilidade com endpoint antigo
@app.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str) -> Dict:
    """Retorna preferências (formato compatível com orchestrator)"""
    try:
        cache_key = _get_preferences_key(user_id)
        prefs = cache.get(cache_key) or {}
        
        # Converter para formato esperado pelo orchestrator
        return {
            "user_id": user_id,
            "explicit": prefs,
            "learned": {},
            "effective": {
                "preferred_categories": prefs.get("interests", []),
                "blocked_categories": prefs.get("blocked_topics", []),
                "preferred_sources": prefs.get("favorite_sources", []),
                "blocked_sources": prefs.get("blocked_sources", []),
                "keywords_boost": prefs.get("interests", []),
                "keywords_block": prefs.get("blocked_topics", [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    )

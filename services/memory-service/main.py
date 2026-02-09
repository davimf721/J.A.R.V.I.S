"""
Memory Service - Microserviço para gerenciamento de memória vetorial
Integra com ChromaDB para armazenamento semântico
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os
from datetime import datetime
import logging

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger
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
    from chromadb.config import Settings
    
    settings = Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMADB_PERSIST_DIR,
        anonymized_telemetry=False
    )
    
    # Usando cliente local
    chroma_client = chromadb.Client(settings)
    logger.info(f"✅ ChromaDB inicializado em {CHROMADB_PERSIST_DIR}")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
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


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8005,
        log_level="info"
    )

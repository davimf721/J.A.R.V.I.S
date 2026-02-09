"""
JARVIS Orchestrator - Coordena a execução do pipeline de podcast
Funciona como o maestro orquestrando todos os microserviços
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional
import sys
import os

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.models import (
    PodcastRequest, PodcastResult, JobStatus, 
    ServiceInfo, ServiceStatus, AgentType
)
from shared.config import SERVICE_URLS, ENABLE_AUTH
from shared.utils import get_logger, ServiceClient, cache
import json

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS Orchestrator",
    description="Coordenador central do pipeline de podcast",
    version="1.0.0"
)

logger = get_logger(__name__)

# Clientes para outros serviços
news_client = ServiceClient(SERVICE_URLS["news_service"])
script_client = ServiceClient(SERVICE_URLS["script_service"])
tts_client = ServiceClient(SERVICE_URLS["tts_service"])
memory_client = ServiceClient(SERVICE_URLS["memory_service"])

# Armazenamento em memória de jobs (em produção usar banco de dados)
active_jobs = {}


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do orchestrator"""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "timestamp": datetime.utcnow().isoformat(),
        "active_jobs": len(active_jobs)
    }


# ==================== ENDPOINTS ====================
@app.post("/api/podcast/generate")
async def generate_podcast(request: PodcastRequest, background_tasks: BackgroundTasks):
    """
    Inicia geração de um podcast
    Retorna imediatamente com o ID do job
    """
    try:
        job_id = request.id
        
        logger.info(f"📻 Iniciando podcast: {job_id} (agente: {request.agent_name})")
        
        # Armazenar job como pendente
        active_jobs[job_id] = {
            "status": "pending",
            "request": request,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Processar em background
        background_tasks.add_task(
            process_podcast_pipeline,
            job_id,
            request
        )
        
        return {
            "job_id": job_id,
            "status": "pending",
            "message": "Podcast em fila de processamento"
        }
    
    except Exception as e:
        logger.error(f"Erro ao iniciar podcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/podcast/status/{job_id}")
async def get_podcast_status(job_id: str):
    """Retorna status de um job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    return active_jobs[job_id]


@app.get("/api/podcast/result/{job_id}")
async def get_podcast_result(job_id: str):
    """Retorna resultado de um podcast completo"""
    # Tentar recuperar do cache primeiro
    cached = cache.get(f"podcast_result:{job_id}")
    if cached:
        logger.info(f"📦 Resultado retornado do cache: {job_id}")
        return cached
    
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    
    job = active_jobs[job_id]
    if job.get("status") != "completed":
        raise HTTPException(
            status_code=202,
            detail=f"Job ainda em processamento. Status: {job.get('status')}"
        )
    
    return job.get("result")


# ==================== PIPELINE ====================
async def process_podcast_pipeline(job_id: str, request: PodcastRequest):
    """
    Pipeline principal: orquestra todos os microserviços
    Fluxo:
    1. Buscar notícias
    2. Recuperar memória relevante
    3. Gerar roteiro
    4. Gerar áudio (TTS)
    5. Salvar resultado
    """
    logger.info(f"▶️  Iniciando pipeline para: {job_id}")
    
    try:
        # Atualizar status
        active_jobs[job_id]["status"] = "running"
        
        # Step 1: Buscar notícias
        logger.info(f"📰 Step 1/4: Buscando notícias...")
        news_response = await news_client.post(
            "/api/news/fetch",
            data={
                "language": request.language,
                "limit": request.news_count
            }
        )
        
        if not news_response:
            raise Exception("Falha ao buscar notícias")
        
        news_list = news_response.get("news", [])
        logger.info(f"✅ {len(news_list)} notícias encontradas")
        
        # Step 2: Recuperar memória relevante
        logger.info(f"🧠 Step 2/4: Buscando memórias relevantes...")
        memory_response = await memory_client.post(
            "/api/memory/recall",
            data={
                "query": f"podcast {request.agent_type.value}",
                "limit": 3,
                "user_id": request.user_id
            }
        )
        
        memory_context = ""
        if memory_response and memory_response.get("memories"):
            memories = memory_response.get("memories", [])
            memory_context = " ".join([m.get("content", "") for m in memories])
            logger.info(f"✅ {len(memories)} memórias recuperadas")
        else:
            logger.info("ℹ️  Nenhuma memória anterior encontrada")
        
        # Step 3: Gerar roteiro
        logger.info(f"📝 Step 3/4: Gerando roteiro...")
        script_response = await script_client.post(
            "/api/script/generate",
            data={
                "agent_name": request.agent_name,
                "agent_type": request.agent_type.value,
                "news": news_list,
                "memory_context": memory_context,
                "language": request.language
            }
        )
        
        if not script_response:
            raise Exception("Falha ao gerar roteiro")
        
        script = script_response.get("script", "")
        logger.info(f"✅ Roteiro gerado ({len(script)} caracteres)")
        
        # Step 4: Gerar áudio (TTS)
        logger.info(f"🎙️  Step 4/4: Gerando áudio...")
        tts_response = await tts_client.post(
            "/api/tts/generate",
            data={
                "text": script,
                "voice": request.voice,
                "agent_name": request.agent_name,
                "language": request.language
            }
        )
        
        if not tts_response:
            raise Exception("Falha ao gerar áudio")
        
        audio_path = tts_response.get("audio_path", "")
        duration = tts_response.get("duration", 0.0)
        logger.info(f"✅ Áudio gerado ({duration:.1f}s)")
        
        # Step 5: Salvar resultado
        result = PodcastResult(
            id=request.id,
            job_id=job_id,
            agent_name=request.agent_name,
            agent_type=request.agent_type,
            status=JobStatus.COMPLETED,
            script=script,
            audio_path=audio_path,
            audio_duration=duration,
            news_used=news_list,
            memory_recalled=memory_context,
            completed_at=datetime.utcnow()
        )
        
        # Cachear resultado
        cache.set(f"podcast_result:{job_id}", result.__dict__, expire_seconds=86400)
        
        # Atualizar job
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["result"] = result.__dict__
        
        logger.info(f"✅ Pipeline concluído: {job_id}")
        
        # Salvar na memória para futuras referências
        await memory_client.post(
            "/api/memory/store",
            data={
                "user_id": request.user_id,
                "content": f"Podcast gerado: {request.agent_name} - {request.agent_type.value}",
                "metadata": {
                    "job_id": job_id,
                    "news_count": len(news_list),
                    "duration": duration,
                    "agent": request.agent_name
                }
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Erro no pipeline: {e}", exc_info=True)
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)


# ==================== DEBUG ENDPOINTS ====================
@app.get("/api/debug/jobs")
async def debug_jobs():
    """Lista todos os jobs (apenas para debug)"""
    return {
        "total_jobs": len(active_jobs),
        "jobs": list(active_jobs.keys()),
        "details": active_jobs
    }


@app.post("/api/debug/test-pipeline")
async def test_pipeline(background_tasks: BackgroundTasks):
    """Inicia um pipeline de teste"""
    request = PodcastRequest(
        agent_name="jarvis_teste",
        agent_type=AgentType.PODCAST_DAILY,
        user_id="test_user",
        news_count=3
    )
    
    background_tasks.add_task(process_podcast_pipeline, request.id, request)
    
    return {"job_id": request.id, "status": "started"}


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8010,
        log_level="info"
    )

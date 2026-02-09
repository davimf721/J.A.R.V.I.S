"""
TTS Service - Microserviço para síntese de voz (Text-to-Speech)
Integra com edge-tts para gerar áudio
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from datetime import datetime
import logging
import asyncio
from pathlib import Path

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, cache
from shared.config import S3_ENDPOINT, S3_BUCKET

# Importar TTS existente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../jarvis-voice'))
try:
    from tts import text_to_speech
except ImportError:
    text_to_speech = None

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS TTS Service",
    description="Serviço de síntese de voz (Text-to-Speech)",
    version="1.0.0"
)

logger = get_logger(__name__)

# Criar diretório de saída
OUTPUT_DIR = Path("/tmp/tts_output")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


# ==================== MODELS ====================
class TTSRequest(BaseModel):
    """Requisição para gerar áudio"""
    text: str
    voice: str = "pt-BR-FranciscaNeural"
    agent_name: str = "jarvis"
    language: str = "pt-BR"
    speed: float = 1.0
    pitch: float = 1.0


class TTSResponse(BaseModel):
    """Resposta com áudio gerado"""
    audio_path: str
    duration: float
    voice: str
    language: str
    size_bytes: int


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    return {
        "status": "healthy",
        "service": "tts-service",
        "timestamp": datetime.utcnow().isoformat(),
        "output_dir": str(OUTPUT_DIR)
    }


# ==================== ENDPOINTS ====================
@app.post("/api/tts/generate")
async def generate_audio(request: TTSRequest) -> TTSResponse:
    """
    Gera áudio a partir de texto usando edge-tts
    """
    try:
        logger.info(f"🎙️  Gerando áudio ({request.voice}, {len(request.text)} chars)...")
        
        # Verificar cache
        cache_key = f"tts:{hash(request.text)}:{request.voice}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("📦 Áudio retornado do cache")
            return TTSResponse(**cached)
        
        # Gerar nome do arquivo
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audio_file = OUTPUT_DIR / f"{request.agent_name}_{timestamp}.mp3"
        
        # Gerar áudio
        if text_to_speech:
            try:
                text_to_speech(request.text, str(audio_file))
                logger.info(f"✅ Áudio gerado: {audio_file}")
            except Exception as e:
                logger.warning(f"Erro ao gerar áudio com função local: {e}")
                # Fallback: usar edge-tts diretamente
                await generate_audio_with_edge_tts(
                    request.text,
                    request.voice,
                    str(audio_file)
                )
        else:
            logger.warning("TTS local indisponível, usando edge-tts direto")
            await generate_audio_with_edge_tts(
                request.text,
                request.voice,
                str(audio_file)
            )
        
        # Obter informações do arquivo
        if not audio_file.exists():
            raise Exception(f"Arquivo de áudio não foi criado: {audio_file}")
        
        file_size = audio_file.stat().st_size
        # Estimativa: ~100 bytes por segundo (MP3 de qualidade média)
        duration = file_size / 100
        
        result = {
            "audio_path": str(audio_file),
            "duration": duration,
            "voice": request.voice,
            "language": request.language,
            "size_bytes": file_size
        }
        
        # Cachear por 30 dias
        cache.set(cache_key, result, expire_seconds=2592000)
        
        return TTSResponse(**result)
    
    except Exception as e:
        logger.error(f"❌ Erro ao gerar áudio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tts/voices")
async def get_available_voices():
    """Lista vozes disponíveis"""
    voices = [
        {"code": "pt-BR-FranciscaNeural", "name": "Francisca (Feminina)", "language": "Português (Brasil)"},
        {"code": "pt-BR-AntonioNeural", "name": "Antonio (Masculino)", "language": "Português (Brasil)"},
        {"code": "en-US-AriaNeural", "name": "Aria (Feminina)", "language": "Inglês (EUA)"},
        {"code": "en-US-GuyNeural", "name": "Guy (Masculino)", "language": "Inglês (EUA)"},
        {"code": "es-ES-ElviraNeural", "name": "Elvira (Feminina)", "language": "Espanhol (Espanha)"},
    ]
    return {"voices": voices, "default": "pt-BR-FranciscaNeural"}


# ==================== HELPER FUNCTIONS ====================
async def generate_audio_with_edge_tts(text: str, voice: str, output_path: str):
    """Gera áudio usando edge-tts diretamente"""
    try:
        from edge_tts import Communicate
        
        logger.info(f"📝 Gerando áudio com edge-tts...")
        
        communicate = Communicate(text, voice, rate="+0%", volume="+0%", pitch="+0Hz")
        await communicate.save(output_path)
        
        logger.info(f"✅ Áudio salvo: {output_path}")
    
    except Exception as e:
        logger.error(f"❌ Erro ao gerar com edge-tts: {e}")
        raise


# ==================== MAIN ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info"
    )

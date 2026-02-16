"""
TTS Service - Microserviço para síntese de voz (Text-to-Speech)
Integra com edge-tts para gerar áudio natural
Inclui processamento de texto para melhor pronúncia e naturalidade
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from datetime import datetime
import logging
import asyncio
from pathlib import Path
import re

# Adicionar shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.utils import get_logger, cache
from shared.config import S3_ENDPOINT, S3_BUCKET

# ==================== SETUP ====================
app = FastAPI(
    title="JARVIS TTS Service",
    description="Serviço de síntese de voz (Text-to-Speech) com naturalidade aprimorada",
    version="2.0.0"
)

logger = get_logger(__name__)

# Criar diretório de saída
OUTPUT_DIR = Path("/tmp/tts_output")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


# ==================== TEXT PROCESSOR ====================
class TextProcessor:
    """Processa texto para melhorar naturalidade da fala"""
    
    # Dicionário de pronúncias especiais (siglas, termos técnicos)
    PRONUNCIATIONS = {
        # Siglas de tecnologia
        "IA": "i á",
        "AI": "êi ai",
        "API": "a p i",
        "APIs": "a p is",
        "GPU": "gê pê u",
        "GPUs": "gê pê us",
        "CPU": "cê pê u",
        "CPUs": "cê pê us",
        "RAM": "rã",
        "SSD": "ésse ésse dê",
        "HD": "agá dê",
        "USB": "u ésse bê",
        "URL": "u érre éle",
        "URLs": "u érre éles",
        "HTML": "agá tê ême éle",
        "CSS": "cê ésse ésse",
        "SQL": "ésse quê éle",
        "IoT": "aiôtê",
        "ML": "ême éle",
        "NLP": "ene éle pê",
        "LLM": "éle éle ême",
        "LLMs": "éle éle êmes",
        "GPT": "gê pê tê",
        "ChatGPT": "chét gê pê tê",
        "OpenAI": "ópen êi ai",
        "AWS": "a dáblio ésse",
        "GCP": "gê cê pê",
        "DevOps": "devóps",
        "GitHub": "guitrábi",
        "LinkedIn": "linquedín",
        "WhatsApp": "uótsép",
        "YouTube": "iutúbi",
        "Netflix": "nétflícs",
        "Spotify": "espotifai",
        "iPhone": "aifôni",
        "Android": "androíde",
        "iOS": "ai ô ésse",
        "macOS": "mék ô ésse",
        "Windows": "uíndous",
        "Linux": "línucs",
        "Ubuntu": "ubúntu",
        "Python": "páiton",
        "JavaScript": "djáva scripti",
        "TypeScript": "táipi scripti",
        "React": "riécti",
        "Node": "nóudi",
        "Docker": "dóquer",
        "Kubernetes": "cubernétis",
        "Terraform": "terrafórm",
        "Wi-Fi": "uai fai",
        "WiFi": "uai fai",
        "Bluetooth": "blutúfi",
        "5G": "cinco gê",
        "4G": "quatro gê",
        "3D": "três dê",
        "2D": "dois dê",
        "OK": "oquêi",
        "CEO": "cê i ô",
        "CTO": "cê tê ô",
        "NFT": "ene éfe tê",
        "NFTs": "ene éfe tês",
        "VR": "vi ar",
        "AR": "ei ar",
        "XR": "écs ar",
        "vs": "vérsus",
        "VS": "vérsus",
        "etc": "etcétera",
        "Etc": "etcétera",
        "ex": "por exemplo",
        "tbm": "também",
        "pq": "porque",
        "vc": "você",
        "vcs": "vocês",
        "tb": "também",
        "qdo": "quando",
        "hj": "hoje",
        "msg": "mensagem",
        # Números e símbolos
        "%": " por cento",
        "R$": "reais",
        "US$": "dólares",
        "$": "dólares",
        "€": "euros",
        "£": "libras",
        "@": "arroba",
        "&": "e",
        "+": "mais",
        "=": "igual",
        "°C": "graus celsius",
        "°F": "graus fahrenheit",
        "km/h": "quilômetros por hora",
        "m/s": "metros por segundo",
        "GB": "gigabáites",
        "MB": "megabáites",
        "TB": "terabáites",
        "KB": "quilobáites",
        "GHz": "gigahértz",
        "MHz": "megahértz",
    }
    
    # Padrões para adicionar pausas naturais
    PAUSE_PATTERNS = [
        # Pausas após pontuação
        (r'\.(?=\s)', '. <break time="600ms"/>'),
        (r'\!(?=\s)', '! <break time="500ms"/>'),
        (r'\?(?=\s)', '? <break time="500ms"/>'),
        (r'\;(?=\s)', '; <break time="400ms"/>'),
        (r'\:(?=\s)', ': <break time="300ms"/>'),
        (r'\,(?=\s)', ', <break time="200ms"/>'),
        # Pausas antes de conectivos
        (r'\s(mas|porém|entretanto|contudo|todavia)\s', ' <break time="200ms"/> \\1 '),
        (r'\s(portanto|logo|assim|então)\s', ' <break time="200ms"/> \\1 '),
        # Pausas em listas
        (r'(\d+)\.\s', '\\1. <break time="300ms"/>'),
    ]
    
    @classmethod
    def process(cls, text: str, use_ssml: bool = True) -> str:
        """Processa texto para melhor naturalidade"""
        
        # 1. Substituir pronúncias especiais
        processed = text
        for term, pronunciation in cls.PRONUNCIATIONS.items():
            # Usar word boundary para evitar substituições parciais
            pattern = r'\b' + re.escape(term) + r'\b'
            processed = re.sub(pattern, pronunciation, processed, flags=re.IGNORECASE)
        
        # 2. Processar números por extenso para melhor leitura
        processed = cls._process_numbers(processed)
        
        # 3. Processar URLs e emails (simplificar)
        processed = cls._simplify_urls(processed)
        
        # 4. Adicionar pausas naturais se usar SSML
        if use_ssml:
            for pattern, replacement in cls.PAUSE_PATTERNS:
                processed = re.sub(pattern, replacement, processed)
            
            # Envolver em tags SSML
            processed = f'<speak>{processed}</speak>'
        
        return processed
    
    @classmethod
    def _process_numbers(cls, text: str) -> str:
        """Melhora leitura de números"""
        # Anos (1990-2099)
        def year_to_words(match):
            year = int(match.group(1))
            if 2000 <= year <= 2099:
                return f"dois mil e {year - 2000}" if year > 2000 else "dois mil"
            return match.group(0)
        
        text = re.sub(r'\b(19\d{2}|20\d{2})\b', year_to_words, text)
        
        # Porcentagens
        text = re.sub(r'(\d+)%', r'\1 por cento', text)
        
        # Decimais com vírgula
        text = re.sub(r'(\d+),(\d+)', r'\1 vírgula \2', text)
        
        return text
    
    @classmethod
    def _simplify_urls(cls, text: str) -> str:
        """Simplifica URLs para leitura"""
        # Remover URLs completas, manter apenas domínio
        def simplify_url(match):
            url = match.group(0)
            # Extrair domínio principal
            domain_match = re.search(r'(?:https?://)?(?:www\.)?([^/\s]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                # Simplificar domínio
                domain = domain.replace('.com.br', ' ponto com ponto br')
                domain = domain.replace('.com', ' ponto com')
                domain = domain.replace('.org', ' ponto org')
                domain = domain.replace('.net', ' ponto net')
                domain = domain.replace('.io', ' ponto i ó')
                return domain
            return url
        
        text = re.sub(r'https?://[^\s]+', simplify_url, text)
        return text


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
    Gera áudio a partir de texto usando edge-tts com naturalidade aprimorada
    """
    try:
        logger.info(f"🎙️  Gerando áudio ({request.voice}, {len(request.text)} chars)...")
        
        # Verificar cache
        cache_key = f"tts:{hash(request.text)}:{request.voice}"
        cached = cache.get(cache_key)
        if cached:
            logger.info("📦 Áudio retornado do cache")
            return TTSResponse(**cached)
        
        # Processar texto para melhor naturalidade
        processed_text = TextProcessor.process(request.text, use_ssml=False)
        logger.info(f"📝 Texto processado para naturalidade")
        
        # Gerar nome do arquivo
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audio_file = OUTPUT_DIR / f"{request.agent_name}_{timestamp}.mp3"
        
        # Gerar áudio com edge-tts (configurações otimizadas para naturalidade)
        await generate_audio_with_edge_tts(
            processed_text,
            request.voice,
            str(audio_file),
            rate=request.speed,
            pitch=request.pitch
        )
        
        # Obter informações do arquivo
        if not audio_file.exists():
            raise Exception(f"Arquivo de áudio não foi criado: {audio_file}")
        
        file_size = audio_file.stat().st_size
        # Estimativa mais precisa: ~16KB por segundo para MP3 128kbps
        duration = file_size / 16000
        
        result = {
            "audio_path": str(audio_file),
            "duration": duration,
            "voice": request.voice,
            "language": request.language,
            "size_bytes": file_size
        }
        
        # Cachear por 30 dias
        cache.set(cache_key, result, expire_seconds=2592000)
        
        logger.info(f"✅ Áudio gerado: {audio_file} ({duration:.1f}s)")
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
async def generate_audio_with_edge_tts(
    text: str, 
    voice: str, 
    output_path: str,
    rate: float = 1.0,
    pitch: float = 1.0
):
    """
    Gera áudio usando edge-tts com configurações otimizadas para naturalidade
    """
    try:
        import edge_tts
        
        logger.info(f"📝 Gerando áudio com edge-tts...")
        
        # Configurar velocidade e tom
        # Rate: -50% a +100%, 0% é normal
        # Velocidade levemente mais lenta para podcast (mais natural)
        rate_percent = int((rate - 1.0) * 100) - 5  # -5% mais lento por padrão
        rate_str = f"{rate_percent:+d}%"
        
        # Pitch: -50Hz a +50Hz, 0Hz é normal
        pitch_hz = int((pitch - 1.0) * 50)
        pitch_str = f"{pitch_hz:+d}Hz"
        
        # Volume levemente aumentado para clareza
        volume_str = "+5%"
        
        communicate = edge_tts.Communicate(
            text, 
            voice,
            rate=rate_str,
            volume=volume_str,
            pitch=pitch_str
        )
        
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

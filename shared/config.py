"""
Configurações compartilhadas entre os microserviços
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ==================== SERVIÇOS ====================
# URLs dos microserviços (para comunicação inter-serviços)
SERVICE_URLS = {
    "api_gateway": os.getenv("API_GATEWAY_URL", "http://api-gateway:8000"),
    "llm_service": os.getenv("LLM_SERVICE_URL", "http://llm-service:8001"),
    "news_service": os.getenv("NEWS_SERVICE_URL", "http://news-service:8002"),
    "script_service": os.getenv("SCRIPT_SERVICE_URL", "http://script-service:8003"),
    "tts_service": os.getenv("TTS_SERVICE_URL", "http://tts-service:8004"),
    "memory_service": os.getenv("MEMORY_SERVICE_URL", "http://memory-service:8005"),
    "orchestrator": os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8010"),
}

# ==================== OLLAMA ====================
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11435/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "kimi-k2.5:cloud")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))

# ==================== BANCO DE DADOS ====================
# PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "jarvis")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "jarvis_secure_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "jarvis_db")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

REDIS_URL = (
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    if REDIS_PASSWORD
    else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)

# ==================== MESSAGE QUEUE ====================
# RabbitMQ / Celery
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "jarvis")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "jarvis_queue_pwd")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "jarvis")

RABBITMQ_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VHOST}"
)

# ==================== ARMAZENAMENTO ====================
# S3 / Minio
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_BUCKET = os.getenv("S3_BUCKET", "jarvis-media")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")

# ChromaDB
CHROMADB_HOST = os.getenv("CHROMADB_HOST", "chromadb")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8000"))
CHROMADB_PERSIST_DIR = os.getenv("CHROMADB_PERSIST_DIR", "/data/chromadb")

# ==================== LOGGING ====================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ==================== API ====================
API_TITLE = "JARVIS AI Platform"
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_DESCRIPTION = "Plataforma de microserviços para geração de podcasts com IA"

# Segurança
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ==================== FEATURES ====================
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "true").lower() == "true"
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
ENABLE_TELEMETRY = os.getenv("ENABLE_TELEMETRY", "false").lower() == "true"

# ==================== PADRÕES ====================
# Número de tentativas para operações resilientes
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "2"))

# Timeout padrão para chamadas HTTP entre serviços
HTTP_TIMEOUT_SECONDS = int(os.getenv("HTTP_TIMEOUT_SECONDS", "30"))

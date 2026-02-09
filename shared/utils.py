"""
Utilitários compartilhados para logging, cache, e comunicação entre serviços
"""
import logging
import httpx
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import redis
from shared.config import REDIS_URL, LOG_LEVEL, LOG_FORMAT, HTTP_TIMEOUT_SECONDS

# ==================== LOGGING ====================
def get_logger(name: str) -> logging.Logger:
    """Retorna um logger configurado"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# ==================== REDIS CACHE ====================
class CacheManager:
    """Gerencador de cache com Redis"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            get_logger(__name__).warning(f"Redis indisponível, cache desabilitado: {e}")
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        if not self.enabled:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            get_logger(__name__).error(f"Erro ao recuperar cache: {e}")
            return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Armazena valor no cache"""
        if not self.enabled:
            return False
        try:
            self.redis_client.setex(
                key,
                expire_seconds,
                json.dumps(value)
            )
            return True
        except Exception as e:
            get_logger(__name__).error(f"Erro ao salvar cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        if not self.enabled:
            return False
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            get_logger(__name__).error(f"Erro ao deletar cache: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Limpa múltiplas chaves por padrão"""
        if not self.enabled:
            return 0
        try:
            cursor = 0
            count = 0
            while True:
                cursor, keys = self.redis_client.scan(cursor, match=pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    count += len(keys)
                if cursor == 0:
                    break
            return count
        except Exception as e:
            get_logger(__name__).error(f"Erro ao limpar cache: {e}")
            return 0


# ==================== HTTP CLIENT ====================
class ServiceClient:
    """Cliente HTTP para comunicação entre microserviços"""
    
    def __init__(self, service_url: str, timeout: int = HTTP_TIMEOUT_SECONDS):
        self.service_url = service_url
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Faz requisição GET"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.service_url}{endpoint}",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Erro em GET {endpoint}: {e}")
            return None
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Faz requisição POST"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.service_url}{endpoint}",
                    json=data,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self.logger.error(f"Erro em POST {endpoint}: {e}")
            return None


# ==================== RETRY LOGIC ====================
async def retry_async(
    func,
    max_retries: int = 3,
    delay_seconds: int = 2,
    backoff: float = 2.0
):
    """Executa função assíncrona com retry exponencial"""
    logger = get_logger(__name__)
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = delay_seconds * (backoff ** attempt)
            logger.warning(
                f"Tentativa {attempt + 1}/{max_retries} falhou, "
                f"aguardando {wait_time}s: {e}"
            )
            
            import asyncio
            await asyncio.sleep(wait_time)


def retry_sync(
    func,
    max_retries: int = 3,
    delay_seconds: int = 2,
    backoff: float = 2.0
):
    """Executa função síncrona com retry exponencial"""
    logger = get_logger(__name__)
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = delay_seconds * (backoff ** attempt)
            logger.warning(
                f"Tentativa {attempt + 1}/{max_retries} falhou, "
                f"aguardando {wait_time}s: {e}"
            )
            
            import time
            time.sleep(wait_time)


# ==================== INICIALIZAÇÃO ====================
cache = CacheManager()
logger = get_logger("jarvis")

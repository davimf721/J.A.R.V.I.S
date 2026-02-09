"""
Shared data models for JARVIS microservices
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class ServiceStatus(str, Enum):
    """Status de saúde do serviço"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class AgentType(str, Enum):
    """Tipos de agentes disponíveis"""
    PODCAST_DAILY = "podcast_daily"
    MARKET_ANALYSIS = "market_analysis"
    EMAIL_SUMMARY = "email_summary"
    CONTENT_GENERATOR = "content_generator"
    CODE_ASSISTANT = "code_assistant"


class JobStatus(str, Enum):
    """Status de um job em execução"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ServiceInfo:
    """Informações básicas de um serviço"""
    name: str
    version: str
    status: ServiceStatus
    timestamp: datetime = field(default_factory=datetime.utcnow)
    uptime_seconds: int = 0


@dataclass
class NewsItem:
    """Item de notícia"""
    title: str
    summary: str
    source: str
    url: str
    published_at: datetime
    language: str = "pt-BR"
    category: Optional[str] = None


@dataclass
class PodcastRequest:
    """Requisição para geração de podcast"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: AgentType = AgentType.PODCAST_DAILY
    agent_name: str = "jarvis"
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    news_count: int = 8
    language: str = "pt-BR"
    voice: str = "pt-BR-FranciscaNeural"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PodcastResult:
    """Resultado da geração de um podcast"""
    id: str
    job_id: str
    agent_name: str
    agent_type: AgentType
    status: JobStatus
    script: Optional[str] = None
    audio_path: Optional[str] = None
    audio_duration: Optional[float] = None
    news_used: List[NewsItem] = field(default_factory=list)
    memory_recalled: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None


@dataclass
class Agent:
    """Configuração de um agente"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: AgentType = AgentType.PODCAST_DAILY
    user_id: str = ""
    enabled: bool = True
    schedule: Optional[str] = None  # cron format
    configuration: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class JobMessage:
    """Mensagem de job para fila de processamento"""
    job_id: str
    agent_id: str
    agent_name: str
    agent_type: AgentType
    user_id: str
    priority: int = 5  # 1-10, 10 é maior prioridade
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

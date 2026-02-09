# JARVIS - Arquitetura de Microserviços

## 📋 Visão Geral

A plataforma JARVIS agora está estruturada como uma arquitetura moderna de microserviços totalmente containerizada. Cada serviço é independente, escalável e pode ser desenvolvido/testado isoladamente.

```
┌─────────────────────────────────────────────────────────────┐
│                    ORQUESTRADOR                              │
│              (Orchestrator - :8010)                          │
└────────────┬────────────────────────────────────────────────┘
             │
   ┌─────────┼─────────┬──────────┬──────────┬──────────┐
   │         │         │          │          │          │
┌──▼──┐  ┌──▼──┐  ┌───▼──┐  ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│LLM  │  │News │  │Script│  │ TTS  │  │Memory│  │Auth  │
│ :80 │  │ :80 │  │ :80  │  │ :80  │  │ :80  │  │ :80  │
│  1  │  │  2  │  │  3   │  │  4   │  │  5   │  │  6   │
└─────┘  └─────┘  └──────┘  └──────┘  └─────┘  └──────┘
   │         │         │          │          │          │
   └─────────┼─────────┴──────────┴──────────┴──────────┘
             │
┌────────────┼────────────────────────────────────────────┐
│   INFRAESTRUTURA DE DADOS                               │
│                                                          │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │
│  │ PostgreSQL │ │  Redis   │ │RabbitMQ  │ │Chromadb│  │
│  │   :5432   │ │  :6379   │ │  :5672   │ │ :8200  │  │
│  └────────────┘ └──────────┘ └──────────┘ └────────┘  │
│                                                          │
│  ┌────────────┐ ┌──────────┐                           │
│  │  Ollama    │ │  Minio   │                           │
│  │ :11435     │ │  :9000   │                           │
│  └────────────┘ └──────────┘                           │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Preparação Inicial

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Criar o arquivo .env (apenas uma vez):
# - Verificar credenciais do PostgreSQL
# - Verificar token do Ollama
# - Outras configurações conforme necessário
```

### 2. Iniciar os Serviços

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f orchestrator

# Parar tudo
docker-compose down
```

### 3. Verificar Saúde dos Serviços

```bash
# Verificar orchestrator
curl http://localhost:8010/health

# Verificar LLM Service
curl http://localhost:8001/health

# Verificar News Service
curl http://localhost:8002/health

# Verificar Script Service
curl http://localhost:8003/health

# Verificar TTS Service
curl http://localhost:8004/health

# Verificar Memory Service
curl http://localhost:8005/health

# Dashboard Grafana
# http://localhost:3000 (admin/admin)

# RabbitMQ Management
# http://localhost:15672 (jarvis/jarvis_queue_pwd)

# Minio Console
# http://localhost:9001 (minioadmin/minioadmin)
```

## 📡 Usar a Plataforma via API

### Gerar um Podcast (Fluxo Completo)

```bash
# 1. Iniciar geração (retorna imediatamente com job_id)
curl -X POST http://localhost:8010/api/podcast/generate \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "jarvis",
    "agent_type": "podcast_daily",
    "user_id": "user_123",
    "news_count": 8,
    "language": "pt-BR",
    "voice": "pt-BR-FranciscaNeural"
  }'

# Resposta:
# {
#   "job_id": "abc-123-def",
#   "status": "pending",
#   "message": "Podcast em fila de processamento"
# }

# 2. Verificar status do job
curl http://localhost:8010/api/podcast/status/abc-123-def

# 3. Recuperar resultado completo (quando pronto)
curl http://localhost:8010/api/podcast/result/abc-123-def
```

### Endpoints Principais do Orchestrator

```
# Podcasts
POST   /api/podcast/generate           # Inicia geração
GET    /api/podcast/status/{job_id}    # Status do job
GET    /api/podcast/result/{job_id}    # Resultado final

# Debug
GET    /api/debug/jobs                 # Lista todos os jobs
POST   /api/debug/test-pipeline        # Testa pipeline

# Health
GET    /health                         # Status do orchestrator
```

## 🔧 Serviços Detalhados

### LLM Service (porta 8001)
- Integração com Ollama
- Geração de texto via IA
- Cache de respostas
- Endpoints: `/api/llm/generate`, `/api/llm/stream`

### News Service (porta 8002)
- Busca de notícias de múltiplas fontes
- Cache de 4 horas
- Deduplicação automática
- Endpoints: `/api/news/fetch`, `/api/news/sources`

### Script Service (porta 8003)
- Geração de roteiros de podcast
- Integração com LLM Service
- Cálculo de duração estimada
- Endpoints: `/api/script/generate`, `/api/script/preview`

### TTS Service (porta 8004)
- Síntese de voz (edge-tts)
- Suporte a múltiplas vozes
- Cache de áudios
- Endpoints: `/api/tts/generate`, `/api/tts/voices`

### Memory Service (porta 8005)
- Armazenamento vetorial (ChromaDB)
- Busca semântica
- Isolamento por usuário
- Endpoints: `/api/memory/store`, `/api/memory/recall`, `/api/memory/{user_id}`

### Orchestrator (porta 8010)
- Coordena todo o pipeline
- Gerencia jobs
- Retorna resultados
- Endpoints: `/api/podcast/*`, `/api/debug/*`

## 📊 Monitoramento

### Prometheus (porta 9090)
```
Acesso: http://localhost:9090

Métricas disponíveis:
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- container_network_io_bytes_total
```

### Grafana (porta 3000)
```
Acesso: http://localhost:3000
User: admin
Pass: admin (altere em .env)

Dashboards pré-configurados:
- Visão geral dos serviços
- CPU e memória por container
- Taxa de requisições
- Erros por serviço
```

## 🗄️ Infraestrutura de Dados

### PostgreSQL (porta 5432)
```
User: jarvis
Password: (veja .env)
Database: jarvis_db

Tabelas (serão criadas via Alembic):
- users
- agents
- jobs
- results
- audit_logs
```

### Redis (porta 6379)
```
Cache para:
- Resultados de LLM
- Notícias (4 horas)
- Roteiros (24 horas)
- Sessões de usuário
```

### RabbitMQ (porta 5672, Management: 15672)
```
Filas:
- podcast.generation
- tts.generation
- email.notifications

User: jarvis
Pass: (veja .env)
Virtual Host: jarvis
```

### ChromaDB (porta 8200)
```
Banco vetorial para memória
Collections por usuário: user_{user_id}
Persistência em: /data/chromadb
```

### Minio (porta 9000, Console: 9001)
```
Bucket: jarvis-media

Armazenagem de:
- Áudios em MP3
- Logs
- Backups
```

### Ollama (porta 11435)
```
Modelos disponíveis:
- kimi-k2.5:cloud (padrão)
- llama2
- mistral
- phi

Para instalar novo modelo:
docker exec jarvis-ollama ollama pull {model_name}
```

## 🔄 Pipeline de Geração de Podcast

1. **Requisição** → Orquestrador recebe POST /api/podcast/generate
2. **Busca de Notícias** → News Service busca de múltiplas fontes
3. **Recuperação de Memória** → Memory Service busca contexto anterior
4. **Geração de Roteiro** → Script Service cria texto com LLM
5. **Síntese de Voz** → TTS Service converte texto em áudio MP3
6. **Armazenamento** → Resultado salvo em Minio
7. **Resposta** → Retorna URL do áudio ao cliente

Tempo aproximado: **3-5 minutos** (depende de Ollama)

## 🆘 Troubleshooting

### Ollama não conecta
```bash
# Verificar se Ollama está rodando
docker logs jarvis-ollama

# Pré-carregar modelo (opcional)
docker exec jarvis-ollama ollama pull kimi-k2.5:cloud

# Aumentar timeout em .env se necessário
LLM_TIMEOUT=600
```

### Serviço não inicia
```bash
# Ver logs detalhados
docker logs {service_name}

# Verificar dependências
docker-compose logs

# Verificar rede
docker network ls
docker network inspect jarvis-network
```

### PostgreSQL não conecta
```bash
# Verificar status
docker exec jarvis-postgres pg_isready

# Ver logs
docker logs jarvis-postgres

# Reset (cuidado - apaga dados!)
docker-compose down -v
docker-compose up -d postgres
```

## 📦 Fazer Build Manual de um Serviço

```bash
# Build de um serviço específico
docker-compose build llm-service

# Build e iniciar
docker-compose up -d --build llm-service

# Build sem cache
docker-compose build --no-cache llm-service
```

## 🛠️ Próximos Passos

1. **API Gateway** - Adicionar autenticação e rate limiting
2. **Worker Queue** - Processar jobs em background com Celery
3. **Webhook** - Notificações quando podcast está pronto
4. **Analytics** - Dashboard de uso por usuário
5. **Scaling** - Múltiplas instâncias com load balancer
6. **Frontend** - Dashboard web para gerenciar agentes

## 📚 Estrutura de Pastas

```
jarvis_local/
├── docker-compose.yml          # Orquestração Docker
├── .env.example               # Template de variáveis
├── .env                       # Variáveis (não commitar!)
│
├── shared/
│   ├── models.py              # Dataclasses compartilhadas
│   ├── config.py              # Configurações globais
│   └── utils.py               # Funções utilitárias
│
├── services/
│   ├── orchestrator/          # API principal
│   ├── llm-service/           # Integração Ollama
│   ├── news-service/          # Busca de notícias
│   ├── script-service/        # Geração de roteiros
│   ├── tts-service/           # Síntese de voz
│   └── memory-service/        # Armazenamento vetorial
│
├── infrastructure/
│   ├── database/
│   │   └── init.sql           # SQL inicial
│   └── monitoring/
│       └── prometheus.yml     # Config Prometheus
│
├── jarvis-core/               # Código legado (ainda suportado)
└── jarvis-voice/              # Código legado (ainda suportado)
```

## 🎯 Comandos Úteis

```bash
# Ver status de todos os serviços
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Parar tudo
docker-compose down

# Remover tudo (incluindo volumes!)
docker-compose down -v

# Executar comando em um container
docker-compose exec orchestrator curl http://localhost:8010/health

# Acessar shell de um container
docker-compose exec orchestrator bash

# Ver uso de recursos
docker stats

# Limpar volumes não utilizados
docker volume prune

# Atualizar imagens
docker-compose pull
docker-compose up -d
```

---

**Documentação versão**: 1.0  
**Data**: Fevereiro 2026  
**Autor**: JARVIS Development Team

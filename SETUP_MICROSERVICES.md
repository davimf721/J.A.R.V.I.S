# JARVIS AI Platform - Arquitetura de Microserviços

## 🎯 Objetivo

Transformar o projeto JARVIS em uma plataforma escalável baseada em **microserviços containerizados**. Cada componente é independente, testável e pronto para produção.

## 📦 O Que Foi Criado

### 1. **Arquitetura de Microserviços** (7 serviços)

```
┌─────────────────────────────────────────┐
│        ORCHESTRATOR (API Central)        │
│         http://localhost:8010            │
└────────┬────────────────────────────────┘
         │
    ┌────┴─────┬──────────┬─────────┬──────────┬──────┐
    │           │          │         │          │      │
┌───▼──┐  ┌───▼──┐  ┌────▼──┐  ┌──▼──┐  ┌────▼──┐ │
│ LLM  │  │News  │  │Script │  │ TTS │  │Memory │ │
│ 8001 │  │ 8002 │  │ 8003  │  │8004 │  │ 8005  │ │
└──────┘  └──────┘  └───────┘  └─────┘  └───────┘ │
                                                    │
└────────────────────────────────────────────────────┘

Todos os serviços rodando em Docker!
```

**Serviços:**
- **Orchestrator** (8010) - Coordena toda a execução
- **LLM Service** (8001) - Integração com Ollama
- **News Service** (8002) - Busca de notícias
- **Script Service** (8003) - Geração de roteiros
- **TTS Service** (8004) - Síntese de voz
- **Memory Service** (8005) - Banco vetorial

### 2. **Infraestrutura de Dados** (6 componentes)

```
┌─────────────────────────────────────────┐
│      INFRAESTRUTURA DE DADOS             │
│                                          │
│  PostgreSQL   Redis      RabbitMQ        │
│    5432       6379        5672           │
│                                          │
│  ChromaDB    Minio       Ollama          │
│    8200      9000        11435           │
└──────────────────────────────────────────┘
```

- **PostgreSQL** - Banco relacional (users, jobs, results)
- **Redis** - Cache (notícias, roteiros, sesões)
- **RabbitMQ** - Fila de mensagens
- **ChromaDB** - Banco vetorial (memória semântica)
- **Minio** - Armazenamento S3-compatível (áudios)
- **Ollama** - LLM local (kimi-k2.5:cloud)

### 3. **Monitoramento** (2 componentes)

- **Prometheus** (9090) - Coleta de métricas
- **Grafana** (3000) - Dashboard visual

### 4. **Código Compartilhado** (Shared)

```
shared/
├── models.py      # Dataclasses para PodcastRequest, NewsItem, etc
├── config.py      # Configurações globais (URLs, credenciais)
└── utils.py       # Logging, cache, retry logic, HTTP client
```

## 🚀 Como Iniciar

### Pré-requisitos
- Docker Desktop instalado
- PowerShell (Windows) ou bash (Linux/Mac)
- ~20GB de espaço em disco (para Ollama + dados)

### Inicialização Rápida

```powershell
# Windows PowerShell
cd jarvis_local
.\start.ps1 start

# Linux/Mac (usar docker-compose diretamente)
cd jarvis_local
docker-compose up -d
```

### Verificar Status

```powershell
# Ver todos os serviços rodando
.\start.ps1 status

# Ou via curl
curl http://localhost:8010/health
curl http://localhost:8001/health
# ... etc
```

### Parar Serviços

```powershell
.\start.ps1 stop
```

## 📡 API - Como Usar

### 1. Gerar um Podcast

```bash
curl -X POST http://localhost:8010/api/podcast/generate \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "jarvis",
    "agent_type": "podcast_daily",
    "user_id": "user_123",
    "news_count": 8,
    "language": "pt-BR"
  }'

# Resposta:
# {
#   "job_id": "123e4567-e89b-12d3-a456-426614174000",
#   "status": "pending"
# }
```

### 2. Verificar Status

```bash
curl http://localhost:8010/api/podcast/status/123e4567-e89b-12d3-a456-426614174000

# Resposta:
# {
#   "status": "running",
#   "request": {...}
# }
```

### 3. Pegar Resultado

```bash
curl http://localhost:8010/api/podcast/result/123e4567-e89b-12d3-a456-426614174000

# Resposta quando pronto:
# {
#   "script": "E aí, Davi. Domingo, 8 de fevereiro...",
#   "audio_path": "/tmp/tts_output/jarvis_20260208_001234.mp3",
#   "audio_duration": 598.5,
#   "news_used": [...],
#   "status": "completed"
# }
```

## 🔌 Endpoints Disponíveis

### Orchestrator (porta 8010)
```
POST   /api/podcast/generate           # Inicia podcast
GET    /api/podcast/status/{job_id}    # Status
GET    /api/podcast/result/{job_id}    # Resultado
GET    /api/debug/jobs                 # Listar jobs
GET    /health                         # Health check
```

### LLM Service (porta 8001)
```
POST   /api/llm/generate               # Gerar texto
GET    /health                         # Health check
```

### News Service (porta 8002)
```
POST   /api/news/fetch                 # Buscar notícias
GET    /api/news/sources               # Listar fontes
GET    /health                         # Health check
```

### Script Service (porta 8003)
```
POST   /api/script/generate            # Gerar roteiro
GET    /api/script/preview             # Preview
GET    /health                         # Health check
```

### TTS Service (porta 8004)
```
POST   /api/tts/generate               # Gerar áudio
GET    /api/tts/voices                 # Listar vozes
GET    /health                         # Health check
```

### Memory Service (porta 8005)
```
POST   /api/memory/store               # Armazenar
POST   /api/memory/recall              # Recuperar
GET    /api/memory/stats/{user_id}     # Estatísticas
GET    /health                         # Health check
```

## 📊 Dashboards

Acessar no navegador:

```
Orchestrator         http://localhost:8010/health
Prometheus           http://localhost:9090
Grafana              http://localhost:3000 (admin/admin)
RabbitMQ             http://localhost:15672 (jarvis/jarvis_queue_pwd)
Minio                http://localhost:9001 (minioadmin/minioadmin)
```

## 🔄 Pipeline Completo

1. **Requisição** → User faz POST /api/podcast/generate
2. **Validação** → Orchestrator valida dados
3. **Busca de Notícias** → News Service busca de 8 fontes
4. **Geração de Roteiro** → Script Service + LLM gera texto
5. **Síntese de Voz** → TTS Service converte em áudio MP3
6. **Armazenamento** → Áudio salvo em Minio (S3)
7. **Retorno** → Orquestrador retorna URL do áudio

**Tempo total**: ~3-5 minutos (depende de Ollama)

## 📝 Estrutura de Pastas

```
jarvis_local/
├── docker-compose.yml          # Orquestração
├── .env.example               # Template
├── start.ps1                  # Script de inicialização
├── MICROSERVICES_GUIDE.md    # Documentação detalhada
│
├── shared/                    # Código compartilhado
│   ├── models.py
│   ├── config.py
│   └── utils.py
│
├── services/                  # Microserviços
│   ├── orchestrator/
│   ├── llm-service/
│   ├── news-service/
│   ├── script-service/
│   ├── tts-service/
│   └── memory-service/
│
├── infrastructure/            # Config de infraestrutura
│   ├── database/
│   │   └── init.sql
│   └── monitoring/
│       └── prometheus.yml
│
├── jarvis-core/              # Código legado (opcional)
└── jarvis-voice/             # Código legado (opcional)
```

## 🆘 Troubleshooting

### Serviço não inicia
```powershell
# Ver logs detalhados
docker logs jarvis-{service-name}

# Rebuildar serviço
.\start.ps1 build
.\start.ps1 start -Rebuild
```

### Ollama não conecta
```powershell
# Verificar se Ollama está rodando
docker logs jarvis-ollama

# Pré-carregar modelo manualmente
docker exec jarvis-ollama ollama pull kimi-k2.5:cloud
```

### Limpar tudo (cuidado!)
```powershell
.\start.ps1 clean  # Remove todos os volumes e dados!
```

## ✅ O Que Funciona Agora

- ✅ Todos os 7 microserviços containerizados
- ✅ Comunicação entre serviços via HTTP
- ✅ Cache com Redis
- ✅ Banco vetorial com ChromaDB
- ✅ Armazenamento com Minio
- ✅ Fila de mensagens (RabbitMQ)
- ✅ Monitoramento (Prometheus + Grafana)
- ✅ Health checks automáticos
- ✅ Docker Compose para orquestração
- ✅ Logging centralizado

## 🔮 Próximos Passos

### Fase 2: Melhorias
- [ ] API Gateway com autenticação JWT
- [ ] Rate limiting por tier
- [ ] Webhooks para notificação
- [ ] Workers de background (Celery)
- [ ] Dashboard web

### Fase 3: Escalabilidade
- [ ] Kubernetes deployment
- [ ] Auto-scaling
- [ ] Load balancer
- [ ] CI/CD pipeline
- [ ] Deploy em nuvem (AWS/GCP/Azure)

### Fase 4: Comercialização
- [ ] Billing system
- [ ] Subscription management
- [ ] White-label options
- [ ] API keys
- [ ] SLA monitoring

## 📚 Documentação

Consulte estes arquivos para detalhes:

- **MICROSERVICES_GUIDE.md** - Guia completo de microserviços
- **BUSINESS_PLAN.md** - Estratégia de monetização
- **.env.example** - Variáveis de ambiente
- **docker-compose.yml** - Configuração Docker

## 💡 Notas Importantes

1. **Ollama**: Requer GPU para performance ideal. Em CPU, leva 3-5 minutos por podcast
2. **Storage**: Os áudios são salvos em Minio (local). Configure S3 real em produção
3. **Database**: PostgreSQL está com dados persistentes em volumes Docker
4. **Cache**: Redis cacheia por 4 horas (notícias) e 24h (roteiros)
5. **Segurança**: Em produção, alterar todas as senhas em .env

## 🎓 Arquitetura Explicada

### Por que Microserviços?

1. **Escalabilidade** - Escalar apenas o serviço que precisa
2. **Resiliência** - Um serviço com problema não derruba tudo
3. **Deploy Independente** - Atualizar um serviço sem afetar outros
4. **Tecnologia Mix** - Cada serviço pode ter stack diferente
5. **Facilita Equipes** - Diferentes times podem trabalhar em paralelo

### Padrões Usados

- **API Gateway** - Orquestrador como ponto de entrada central
- **Service Discovery** - Docker network para encontrar serviços
- **Circuit Breaker** - Retry logic em utils.py
- **Caching** - Redis para reduzir latência
- **Event Driven** - RabbitMQ para operações assíncronas
- **Health Checks** - Todos os serviços implementam /health

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte MICROSERVICES_GUIDE.md
2. Verifique logs: `.\start.ps1 logs`
3. Teste individual: `curl http://localhost:{porta}/health`
4. Limpe e comece: `.\start.ps1 clean && .\start.ps1 start`

---

**Versão**: 1.0 Beta  
**Data**: Fevereiro 2026  
**Status**: Pronto para testes em ambiente de desenvolvimento

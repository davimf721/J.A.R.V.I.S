# JARVIS - Sistema de Podcast Inteligente

Sistema de **geração automática de podcasts** baseado em inteligência artificial, utilizando arquitetura de microserviços em Docker.

## 🎯 Visão Geral

JARVIS é uma plataforma que:

- 📰 **Busca notícias** automaticamente da internet
- 🤖 **Processa com IA** usando modelos LLM locais (Ollama)
- 📝 **Gera roteiros** de podcast dinamicamente
- 🎙️ **Sintetiza voz** em português
- 💾 **Armazena embeddings** vetoriais para busca semântica
- 🔄 **Orquestra fluxos** complexos entre serviços
- 🗄️ **Persiste dados** em PostgreSQL
- ⚡ **Cacheia resultados** com Redis

---

## 🏗️ Arquitetura

### Microserviços (6 serviços FastAPI)

| Serviço | Porta | Função |
|---------|-------|--------|
| **llm-service** | 8001 | Integração com Ollama/LLM local |
| **news-service** | 8002 | Busca e processamento de notícias |
| **script-service** | 8003 | Geração dinâmica de roteiros |
| **tts-service** | 8004 | Síntese de voz (Text-to-Speech) |
| **memory-service** | 8005 | Vector embeddings (ChromaDB) |
| **orchestrator** | 8010 | Orquestração de fluxos |

### Infraestrutura (6 serviços)

| Serviço | Porta | Função |
|---------|-------|--------|
| **Ollama** | 11435 | LLM local (modelos IA) |
| **PostgreSQL** | 5432 | Banco de dados principal |
| **Redis** | 6379 | Cache em memória |
| **RabbitMQ** | 5672 | Message broker (filas) |
| **ChromaDB** | 8000 | Vector database |
| **MinIO** | 9000 | Object storage (S3-compatible) |

### Módulos Compartilhados

```
shared/
 ├─ config.py      # Configurações centralizadas
 ├─ models.py      # Modelos Pydantic
 └─ utils.py       # Funções utilitárias
```

---

## 🚀 Quick Start

### Opção 1: GitHub Codespace (Sem Espaço Local) ⭐ RECOMENDADO

```bash
# 1. Criar Codespace (GitHub web)
# 2. No terminal do Codespace:
docker-compose up -d --build

# 3. Aguarde 5-10 minutos
# 4. Verificar:
docker-compose ps
```

**Vantagens:**
- ✅ Grátis (60h/mês)
- ✅ Sem espaço em disco
- ✅ Setup automático

### Opção 2: Windows Local (Com 20GB+ Livres)

```powershell
# Abra PowerShell como Administrador
.\init-windows.ps1
```

O script automaticamente:
- Valida Docker/docker-compose
- Verifica espaço em disco
- Executa build e inicialização
- Verifica saúde dos serviços

**Tempo:** 10-30 minutos (primeira vez)

---

## 📊 Comparação de Ambientes

| Aspecto | Codespace | Windows Local |
|---------|-----------|---------------|
| Setup | 1 comando | 1 script |
| Tempo | 5-10 min | 10-30 min |
| Espaço | 0 GB | 20 GB |
| Custo | Grátis* | Grátis |
| Ideal para | Teste agora | Desenvolvimento |

*60 horas/mês gratuitas

---

## 📚 Documentação

- **QUICKSTART.md** - Comparação rápida de ambientes
- **CODESPACE_GUIDE.md** - Guia completo do Codespace
- **CODESPACE.md** - Comandos essenciais
- **TROUBLESHOOTING.md** - Problemas comuns
- **docker-compose.yml** - Definição dos serviços

---

## 🔧 Comandos Essenciais

### Iniciar Sistema

**Codespace:**
```bash
docker-compose up -d --build
```

**Windows:**
```powershell
.\init-windows.ps1
```

### Monitorar Progresso

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço
docker-compose logs -f llm-service

# Ver status dos containers
docker-compose ps
```

### Testar Saúde

```bash
# Testar um serviço
curl http://localhost:8001/health
curl http://localhost:8010/health
```

### Parar Sistema

```bash
# Parar (mantém dados)
docker-compose down

# Parar e remover tudo
docker-compose down -v
```

---

## 📋 Requisitos

### GitHub Codespace
- Conta GitHub
- Navegador moderno
- Conexão internet

### Windows Local
- Docker Desktop 29.0+
- docker-compose 2.0+
- Windows PowerShell 5.1
- **20GB+ espaço livre em C:**
- Internet (para download de imagens)

---

## ✅ Verificar Que Funcionou

Aguarde 5-10 minutos e execute:

```bash
# Status dos containers
docker-compose ps
# Esperado: Todos com status "Up"

# Testar um endpoint
curl http://localhost:8001/health
# Esperado: HTTP 200 com status "healthy"
```

---

## 🐛 Troubleshooting

### Build falhou?
```bash
docker-compose logs  # Ver erro completo
docker-compose down -v      # Resetar
docker-compose up -d --build  # Tentar novamente
```

### Espaço em disco crítico?
```bash
docker system prune -a
docker image prune -a
```

### Porta já em uso?
```bash
docker ps            # Ver containers
docker kill <id>     # Parar container
```

Consulte **TROUBLESHOOTING.md** para mais problemas.

---

## 📁 Estrutura do Projeto

```
jarvis_local/
├── services/                # 6 microserviços FastAPI
│   ├── llm-service/
│   ├── news-service/
│   ├── memory-service/
│   ├── script-service/
│   ├── tts-service/
│   └── orchestrator/
├── shared/                  # Código compartilhado
│   ├── config.py
│   ├── models.py
│   └── utils.py
├── infrastructure/          # Configurações de infra
│   ├── database/
│   └── monitoring/
├── docker-compose.yml       # Orquestração Docker
├── .dockerignore           # Otimizações de build
├── init-windows.ps1        # Script Windows
├── init-codespace.sh       # Script Linux
└── README.md              # Este arquivo
```

---

## 🔄 Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────────┐
│   Cliente (API ou aplicação)                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│   Orchestrator (porta 8010)                         │
│   - Roteia requisições                              │
│   - Coordena fluxos                                 │
└─────────────────────┬───────────────────────────────┘
                      │
      ┌──────────────┼──────────┬──────────────┐
      ▼              ▼          ▼              ▼
   LLM        News       Script         Memory Service
   Service    Service    Service        │
   │          │         │              │
   └──────────┼─────────┼──────────────┘
              ▼
         ┌──────────────────────────┐
         │  Infraestrutura          │
         ├──────────────────────────┤
         │  Ollama (LLM)            │
         │  PostgreSQL              │
         │  Redis                   │
         │  ChromaDB                │
         │  RabbitMQ                │
         │  MinIO                   │
         └──────────────────────────┘
```

---

## 💡 Próximos Passos

1. **Escolher ambiente:**
   - Codespace = comece AGORA
   - Windows Local = quando tiver espaço

2. **Executar inicialização:**
   - Aguarde 5-10 minutos (Codespace)
   - Aguarde 10-30 minutos (Windows)

3. **Testar um serviço:**
   ```bash
   curl http://localhost:8001/health
   ```

4. **Explorar APIs:**
   - Documentação gerada: `/docs` (Swagger)
   - Exemplos em: `services/[name]/main.py`

5. **Desenvolver:**
   - Modifique código em `services/`
   - Rebuild: `docker-compose up -d --build [service]`
   - Teste: `docker-compose logs -f [service]`

---

## 📞 Suporte

Problemas?

1. Consulte **TROUBLESHOOTING.md**
2. Verifique logs: `docker-compose logs`
3. Tente resetar: `docker-compose down -v && docker-compose up -d --build`

---

## 📝 Notas

- **Modelos antigos:** Pastas `jarvis-core/` e `jarvis-voice/` mantidas localmente para comparação, não vão para GitHub (.gitignore)
- **Dados Docker:** Volumes persistem mesmo após `docker-compose down`
- **Performance:** Primeira execução é lenta (downloads + compilação), subsequentes são rápidas
- **Escalabilidade:** Arquitetura preparada para múltiplas instâncias

---

**Versão:** 2.0  
**Última atualização:** 2026-02-09  
**Status:** Pronto para produção local

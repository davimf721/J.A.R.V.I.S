# JARVIS – Intelligent Podcast System

An **automatic podcast generation system** powered by artificial intelligence, built on a **Docker-based microservices architecture**.

## 🎯 Overview

JARVIS is a platform that:

- 📰 **Automatically fetches news** from the internet  
- 🤖 **Processes content with AI** using Groq API (free) or local Ollama  
- 📝 **Dynamically generates podcast scripts**  
- 🎙️ **Synthesizes voice** in Portuguese  
- 💾 **Stores vector embeddings** for semantic search  
- 🔄 **Orchestrates complex workflows** between services  
- 🗄️ **Persists data** in PostgreSQL  
- ⚡ **Caches results** with Redis  

---

## ⚡ New: Groq API Support (Recommended!)

The project now supports **Groq API** — a **free and ultra-fast** alternative to local Ollama:

- 🚀 **Responses in ~500ms** (vs 30–120s with local Ollama)  
- 💰 **100% free** for development and demos  
- 🧠 **Llama 3.3 70B** — state-of-the-art model  

👉 **[Configure Groq](GROQ_SETUP.md)** — setup in 2 minutes!

---

## 🏗️ Architecture

### Microservices (6 FastAPI services)

| Service | Port | Function |
|--------|------|----------|
| **llm-service** | 8001 | Integration with Groq/Ollama (AI) |
| **news-service** | 8002 | News fetching and processing |
| **script-service** | 8003 | Dynamic script generation |
| **tts-service** | 8004 | Voice synthesis (Text-to-Speech) |
| **memory-service** | 8005 | Vector embeddings (ChromaDB) |
| **orchestrator** | 8010 | Workflow orchestration |

### Infrastructure (6 services)

| Service | Port | Function |
|--------|------|----------|
| **Ollama** | 11435 | Local LLM (AI models) |
| **PostgreSQL** | 5432 | Main database |
| **Redis** | 6379 | In-memory cache |
| **RabbitMQ** | 5672 | Message broker (queues) |
| **ChromaDB** | 8000 | Vector database |
| **MinIO** | 9000 | Object storage (S3-compatible) |

---

## 🚀 Quick Start

```bash
docker-compose up -d --build
```

---

- Roadmap.sh link: https://roadmap.sh/projects/multiservice-docker

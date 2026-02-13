# 🎙️ JARVIS - Setup Completo & Guia de Uso

**Última atualização:** 13 de fevereiro de 2026

---

## ⚡ TL;DR (Resumo Super Rápido)

Se você tem pressa, execute apenas:

```bash
# 1. Instalar e configurar TUDO
chmod +x setup-mac.sh
./setup-mac.sh

# 2. Gerar seu primeiro podcast
./quick-podcast.sh

# 3. Pronto! 🎉
```

---

## 📋 Pré-requisitos

- **macOS 10.15+** (Intel ou Apple Silicon)
- **10GB de espaço em disco** (15GB recomendado)
- **Conexão de internet** (para baixar Docker e modelos)

---

## 🚀 Instalação Completa (Passo 1)

### Execute o Script de Setup Único

```bash
chmod +x setup-mac.sh
./setup-mac.sh
```

**O que vai acontecer:**

1. ✅ Verifica macOS
2. ✅ Instala Xcode Command Line Tools (se necessário)
3. ✅ Instala Homebrew (se necessário)  
4. ✅ Instala Docker Desktop (se necessário)
5. ✅ Inicia Docker
6. ✅ Cria arquivo `.env` com configurações padrão
7. ✅ Constrói imagens Docker
8. ✅ Inicia 12 contêineres:
   - 6 serviços de infraestrutura (Ollama, PostgreSQL, Redis, RabbitMQ, ChromaDB, MinIO)
   - 6 microserviços (LLM, News, Script, TTS, Memory, Orchestrator)
   - 2 ferramentas de monitoramento (Prometheus, Grafana)
9. ✅ Espera todos os serviços ficarem prontos
10. ✅ Mostra instruções finais

**Tempo esperado:** 10-30 minutos

**Se der erro:** Verifique [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🎙️ Gerando Seu Primeiro Podcast (Passo 2)

### Opção A: Interface Interativa (Recomendado)

```bash
./quick-podcast.sh --wait
```

Escolha opções:
- Nome do agente (padrão: JARVIS)
- Tipo (news_anchor, storyteller, analyst)
- Duração (minutos)
- Categoria (tech, business, health, general)

### Opção B: Linha de Comando

```bash
# Podcast padrão
./quick-podcast.sh

# Podcast de 10 minutos, storyteller
./quick-podcast.sh --type storyteller --duration 10

# Podcast de tech, e aguardar conclusão
./quick-podcast.sh --category tech --wait

# Podcast em inglês
./quick-podcast.sh --language en-US
```

### Opção C: Menu Interativo Avançado

```bash
./run-podcast.sh
# Menu com 7 opções
```

### Opção D: API REST Direct

```bash
curl -X POST http://localhost:8010/api/podcast/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "meu_primeiro_podcast",
    "agent_name": "JARVIS",
    "agent_type": "news_anchor",
    "language": "pt-BR",
    "podcast_duration_minutes": 8
  }'
```

---

## 📊 Monitorando o Processo

**Ver status em tempo real:**

```bash
# Ver status dos contêineres
docker-compose ps

# Ver logs do orchestrator
docker-compose logs -f orchestrator

# Ver logs de um serviço específico
docker-compose logs -f llm-service
docker-compose logs -f tts-service
```

**Dashboard de monitoramento:**

- 🔗 [Grafana](http://localhost:3000) - Métricas (admin / admin)
- 🔗 [Prometheus](http://localhost:9090) - Queries de métricas
- 🔗 [RabbitMQ](http://localhost:15672) - Filas (jarvis / jarvis_queue_pwd)
- 🔗 [MinIO](http://localhost:9001) - Storage (minioadmin / minioadmin)

---

## 🎯 Fluxo Completo da Geração

Quando você gera um podcast, isto é o que acontece:

```
1. Requisição enviada ao Orchestrator (porta 8010)
   ↓
2. Step 1: News Service busca notícias (porta 8002)
   ↓
3. Step 2: Memory Service busca contexto semântico (porta 8005)
   ↓
4. Step 3: Script Service gera roteiro com LLM (porta 8003)
   - Chamando LLM Service (porta 8001)
   - Que chama Ollama (porta 11435)
   ↓
5. Step 4: TTS Service sintetiza voz (porta 8004)
   ↓
6. Step 5: Resultado salvo em MinIO (porta 9000)
   ↓
7. Áudio disponível para download

⏱️ Tempo total: 2-5 minutos
```

---

## 🔧 Gerenciamento de Serviços

### Script Gerenciador

```bash
./manage.sh <comando>
```

**Comandos disponíveis:**

```bash
./manage.sh start          # Inicia todos os serviços
./manage.sh stop           # Para todos os serviços
./manage.sh restart        # Reinicia todos
./manage.sh status         # Mostra status
./manage.sh logs           # Ver logs tempo real
./manage.sh logs llm-service   # Logs de um serviço
./manage.sh health         # Verificar saúde
./manage.sh clean          # Remove containers (⚠️ CUIDADO!)
./manage.sh rebuild        # Reconstrói imagens
./manage.sh shell llm-service  # Acesso ao container
```

### Comandos Docker Nativos

```bash
# Docker Compose direto
docker-compose ps              # Ver contêineres
docker-compose up -d           # Iniciar
docker-compose down            # Parar
docker-compose restart service # Reiniciar um serviço
docker-compose logs -f         # Ver logs
```

---

## 🔐 Configuração de Produção

Se você vai usar isto em produção:

### 1. Editar `.env`

```bash
nano .env
```

Mudar estas variáveis:

```env
# Segurança
SECRET_KEY=sua_chave_secreta_aleatoria_muito_longa_aqui

# Banco de dados
POSTGRES_PASSWORD=sua_senha_super_forte_aqui
REDIS_PASSWORD=sua_senha_redis_forte

# Autenticação
ENABLE_AUTH=true
ENABLE_RATE_LIMITING=true

# Logging
LOG_LEVEL=WARNING
```

### 2. Usar HTTPS

```bash
# Configurar reverse proxy (nginx, traefik, etc)
# Ver docker-compose.prod.yml (se existir)
```

### 3. Backup

```bash
# Backup do PostgreSQL
docker-compose exec postgres pg_dump -U jarvis jarvis_db > backup.sql

# Backup de volumes
docker run --rm -v jarvis_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/backup_$(date +%Y%m%d).tar.gz /data
```

---

## 📚 Documentação Completa

| Documento | Conteúdo |
|-----------|----------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Guia detalhado de uso |
| **[API_GUIDE.md](API_GUIDE.md)** | Documentação completa da API REST |
| **[README.md](README.md)** | Visão geral da arquitetura |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Resolução de problemas |
| **.env.example** | Todas as variáveis de configuração |

---

## 🐛 Problemas Comuns & Soluções

### "Docker não encontrado"
```bash
open -a Docker  # Abrir Docker Desktop manualmente
sleep 30        # Aguardar iniciar
./setup-mac.sh  # Continuar
```

### "Serviços não ficam prontos"
```bash
# Verificar logs
docker-compose logs llm-service
docker-compose logs postgres

# Reiniciar tudo
docker-compose down -v
./setup-mac.sh
```

### "Espaço em disco insuficiente"
```bash
# Limpar
docker system prune -a --volumes
```

### "Ollama não responde"
```bash
# Puxar modelo manualmente
docker-compose exec ollama ollama pull kimi-k2.5:cloud

# Ou esperar - vai fazer sozinho na primeira requisição
```

---

## 💡 Dicas & Tricks

### Gerar Podcast Contínuo

```bash
# Script bash para gerar 5 podcasts
for i in {1..5}; do
  echo "Podcast $i/5"
  ./quick-podcast.sh --category tech --wait
  sleep 10
done
```

### Usar Modelo LLM Diferente

```bash
# Editar .env
OLLAMA_MODEL=mistral:latest

# Reiniciar
docker-compose restart llm-service

# Testar
curl -X POST http://localhost:8001/api/llm/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Olá!"}'
```

### Exportar Logs

```bash
# Logs completos
docker-compose logs > logs.txt

# Logs de um serviço
docker-compose logs orchestrator > logs_orchestrator.txt
```

### Usar em Python

```python
import requests

response = requests.post(
    'http://localhost:8010/api/podcast/generate',
    json={
        'id': 'podcast_python',
        'agent_name': 'Bot Python',
        'language': 'pt-BR'
    }
)
print(response.json())
```

---

## 🎯 Arquitetura em Poucas Palavras

```
┌─────────────────────────────────────────────────────┐
│                    Usuário                          │
├─────────────────────────────────────────────────────┤
│  API REST (HTTP)                                    │
│  Orchestrator :8010 - Coordena tudo                │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    [News]      [LLM Service]    [TTS Service]
    :8002       :8001 →          :8004
    busca       Ollama:11435     edge-tts
    notícias              │
        │              [Memory]
        │              :8005
        │              ChromaDB
        │
    [Banco de Dados]
    
    PostgreSQL:5432  -  Redis:6379  -  RabbitMQ:5672
    Banco         Cache          Filas
```

---

## ✨ Funcionalidades Principais

✅ **Busca de Notícias** - Automaticamente coleta notícias de múltiplas fontes  
✅ **IA Local** - Roda modelo LLM localmente via Ollama  
✅ **Geração de Roteiros** - Cria scripts dinâmicos próprios para cada podcast  
✅ **Síntese de Voz** - Converte texto em áudio natural com edge-tts  
✅ **Memória Semântica** - Lembra-se de contexto anterior com ChromaDB  
✅ **Escalável** - Arquitetura de microserviços com Docker  
✅ **Resiliente** - Retry automático, cache, health checks  
✅ **Observável** - Prometheus, Grafana, logs estruturados  
✅ **API REST** - Use via HTTP, Python, NodeJS, etc  

---

## 🚦 Roadmap Próximos Passos

Após ter tudo funcionando:

- [ ] Customizar tipos de agentes
- [ ] Configurar fontes de notícias personalizadas
- [ ] Integrar com seu sistema existente
- [ ] Configurar backup automático
- [ ] Adicionar mais idiomas
- [ ] Deploy em produção
- [ ] Monitorar métricas no Grafana

---

## 📞 Suporte & Ajuda

1. **Verifique logs:** `docker-compose logs | grep ERROR`
2. **Leia documentação:** Veja os `.md` files na raiz
3. **Teste conectividade:** `./quick-podcast.sh`
4. **Resete tudo:** `docker-compose down -v && ./setup-mac.sh`

---

## 🙏 Obrigado!

Você agora tem um **sistema de geração de podcasts com IA** completamente funcional rodando no seu Mac!

**Próximas ações:**

```bash
# 1. Se ainda não fez o setup
./setup-mac.sh

# 2. Gere um podcast
./quick-podcast.sh

# 3. Gerencie serviços
./manage.sh status
```

---

**Enjoy! 🎙️ 🎵 🚀**


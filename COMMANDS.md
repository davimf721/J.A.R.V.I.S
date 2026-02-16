# 🎙️ JARVIS - Guia de Comandos

## Inicialização dos Serviços

### Iniciar todos os serviços
```bash
docker compose up -d
```

### Verificar status dos serviços
```bash
docker compose ps
```

### Ver logs de todos os serviços
```bash
docker compose logs -f
```

### Ver logs de um serviço específico
```bash
docker compose logs -f orchestrator
docker compose logs -f news-service
docker compose logs -f script-service
docker compose logs -f tts-service
docker compose logs -f memory-service
docker compose logs -f llm-service
```

### Parar todos os serviços
```bash
docker compose down
```

### Reiniciar um serviço específico
```bash
docker compose restart orchestrator
```

---

## 🎙️ Criação de Podcasts

### Método Rápido (Script)
```bash
# Podcast padrão (8 minutos, português) - aguarda e baixa o arquivo
bash quick-podcast.sh --wait

# Podcast com nome personalizado (arquivo será salvo como MeuPodcast_DATA.mp3)
bash quick-podcast.sh --name "MeuPodcast" --wait

# Podcast com duração específica
bash quick-podcast.sh --duration 10 --wait

# Podcast em inglês
bash quick-podcast.sh --language en-US --wait

# Podcast com todas as opções
bash quick-podcast.sh --name "TechNews" --type podcast_daily --duration 12 --language pt-BR --wait

# Salvar em diretório específico
bash quick-podcast.sh --name "MeuPodcast" --output /home/user/podcasts --wait
```

**Tipos disponíveis:**
- `podcast_daily` - Podcast diário com análise e opinião sobre as notícias
- `market_analysis` - Análise de mercado e impacto em investimentos tech
- `content_generator` - Conteúdo educativo com explicações profundas
- `email_summary` - Briefing executivo rápido (3 min)
- `code_assistant` - Dev Talk: podcast técnico para desenvolvedores

**Exemplos de cada tipo:**
```bash
# Podcast padrão com comentários e opinião
bash quick-podcast.sh --type podcast_daily --wait

# Análise de mercado para investidores
bash quick-podcast.sh --type market_analysis --name "TechMarket" --wait

# Conteúdo educativo
bash quick-podcast.sh --type content_generator --name "TechExplica" --wait

# Briefing executivo rápido
bash quick-podcast.sh --type email_summary --duration 3 --wait

# Para desenvolvedores
bash quick-podcast.sh --type code_assistant --name "DevTalk" --wait
```

### Método via API (curl)

#### 1. Criar um podcast
```bash
curl -X POST http://localhost:8010/api/podcast/generate \
  -H "Content-Type: application/json" \
  -d '{
    "id": "meu-podcast-001",
    "agent_name": "JARVIS",
    "agent_type": "podcast_daily",
    "language": "pt-BR",
    "news_count": 8,
    "user_id": "davi"
  }'
```

#### 2. Verificar status do podcast
```bash
curl http://localhost:8010/api/podcast/status/meu-podcast-001
```

#### 3. Obter resultado completo
```bash
curl http://localhost:8010/api/podcast/result/meu-podcast-001
```

---

## 📰 Gerenciamento de Notícias

### Buscar notícias manualmente
```bash
curl -X POST http://localhost:8002/api/news/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "language": "pt-BR",
    "limit": 10
  }'
```

### Ver fontes de notícias disponíveis
```bash
curl http://localhost:8002/api/news/sources
```

### Limpar cache de notícias
```bash
curl -X POST http://localhost:8002/api/news/clear-cache
```

---

## 🧠 Sistema de Preferências (Aprendizado)

### 🚀 Método Rápido (Script)

O JARVIS possui um script dedicado para feedback, muito mais simples de usar:

```bash
# Ver ajuda
./feedback.sh help

# Avaliar último podcast (nota 1-5)
./feedback.sh rate 5

# Avaliar e indicar notícias específicas
# Formato: rate <nota> "<gostei>" "<não gostei>"
./feedback.sh rate 4 "1,3" "2"   # Gostou das notícias 1 e 3, não gostou da 2

# Adicionar interesse
./feedback.sh add "inteligência artificial"
./feedback.sh add python
./feedback.sh add kubernetes

# Bloquear tópico
./feedback.sh block política
./feedback.sh block celebridades

# Ver suas preferências atuais
./feedback.sh show

# Ver notícias do último podcast (para saber quais avaliar)
./feedback.sh news
```

### 📊 Via API (curl)

#### Adicionar interesse
```bash
curl -X POST http://localhost:8005/api/interests/add \
  -H "Content-Type: application/json" \
  -d '{"user_id": "davi", "topic": "inteligência artificial"}'
```

#### Bloquear tópico
```bash
curl -X POST http://localhost:8005/api/interests/block \
  -H "Content-Type: application/json" \
  -d '{"user_id": "davi", "topic": "política"}'
```

#### Avaliar podcast
```bash
curl -X POST http://localhost:8005/api/podcast/rate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "davi",
    "podcast_id": "podcast-001",
    "rating": 5,
    "liked_news": [1, 3, 5],
    "disliked_news": [2]
  }'
```

#### Ver notícias do último podcast
```bash
curl http://localhost:8005/api/podcast/last/davi
```

#### Ver preferências
```bash
curl http://localhost:8005/api/interests/davi
```

#### Limpar preferências
```bash
curl -X DELETE http://localhost:8005/api/preferences/davi
```

### 🎯 Como o Sistema Aprende

1. **Interesses**: Tópicos que você adiciona recebem prioridade nas notícias
2. **Bloqueio**: Tópicos bloqueados são automaticamente filtrados
3. **Rating**: A nota do podcast ajusta a seleção geral
4. **Notícias específicas**: Quando você indica notícias que gostou/não gostou, o sistema aprende:
   - Fonte da notícia (ex: TechCrunch, Hacker News)
   - Palavras-chave do título
   - Categoria do assunto

---

## 🔊 Texto para Fala (TTS)

### Gerar áudio de um texto
```bash
curl -X POST http://localhost:8004/api/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Olá! Este é um teste do sistema de texto para fala do JARVIS.",
    "voice": "pt-BR-FranciscaNeural",
    "language": "pt-BR",
    "agent_name": "JARVIS"
  }'
```

### Vozes disponíveis
| Idioma | Voz | Descrição |
|--------|-----|-----------|
| pt-BR | pt-BR-FranciscaNeural | Feminina, natural |
| pt-BR | pt-BR-AntonioNeural | Masculina, natural |
| en-US | en-US-JennyNeural | Feminina, americana |
| en-US | en-US-GuyNeural | Masculina, americana |
| es-ES | es-ES-ElviraNeural | Feminina, espanhola |

---

## 💾 Gerenciamento de Memória

### Armazenar uma memória
```bash
curl -X POST http://localhost:8005/api/memory/store \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "davi",
    "content": "Usuário prefere podcasts sobre IA e programação",
    "category": "preference",
    "metadata": {"topic": "ai", "importance": "high"}
  }'
```

### Recuperar memórias relevantes
```bash
curl -X POST http://localhost:8005/api/memory/recall \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "davi",
    "query": "preferências de podcast",
    "limit": 5
  }'
```

### Ver estatísticas de memória
```bash
curl http://localhost:8005/api/memory/stats/davi
```

### Limpar memória do usuário
```bash
curl -X DELETE http://localhost:8005/api/memory/davi
```

---

## 🤖 LLM Service

### Gerar texto com LLM
```bash
curl -X POST http://localhost:8001/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explique o que é inteligência artificial em 3 frases",
    "context": "Explicação para leigos",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

---

## 🔍 Health Checks

### Verificar saúde de todos os serviços
```bash
# Orchestrator
curl http://localhost:8010/health

# News Service
curl http://localhost:8002/health

# Script Service
curl http://localhost:8003/health

# TTS Service
curl http://localhost:8004/health

# Memory Service
curl http://localhost:8005/health

# LLM Service
curl http://localhost:8001/health
```

---

## 🛠️ Comandos de Manutenção

### Reconstruir todos os containers
```bash
docker compose build --no-cache
docker compose up -d
```

### Limpar tudo e recomeçar
```bash
docker compose down -v
docker system prune -f
docker compose up -d --build
```

### Ver uso de recursos
```bash
docker stats
```

---

## 📊 Monitoramento

### Prometheus (Métricas)
```
http://localhost:9090
```

### Grafana (Dashboards)
```
http://localhost:3000
Usuário: admin
Senha: admin
```

### RabbitMQ (Filas)
```
http://localhost:15672
Usuário: guest
Senha: guest
```

---

## 📝 Exemplo Completo: Criar Podcast Personalizado

```bash
# 1. Definir suas preferências
curl -X PUT http://localhost:8005/api/preferences/davi \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_categories": ["ai", "programming", "cloud"],
    "keywords_boost": ["python", "kubernetes", "openai", "llm"]
  }'

# 2. Criar o podcast (vai baixar automaticamente)
bash quick-podcast.sh --name "TechDaily" --duration 10 --wait

# 3. O sistema automaticamente:
#    - Busca notícias filtradas pelas suas preferências
#    - Prioriza assuntos que você gosta
#    - Evita temas que você não gosta
#    - Gera um roteiro personalizado
#    - Cria o áudio
#    - Baixa o arquivo MP3 para a pasta atual
#    - Salva também o roteiro em TXT

# 4. Dar feedback após ouvir
curl -X POST http://localhost:8005/api/preferences/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "davi",
    "news_title": "OpenAI lança novo modelo GPT-5",
    "category": "ai",
    "feedback": "like"
  }'
```

---

## 🆘 Troubleshooting

### Serviço não inicia
```bash
docker compose logs nome-do-servico
```

### Limpar e reiniciar completamente
```bash
docker compose down -v
docker compose up -d --build
```

### Verificar conectividade entre serviços
```bash
docker compose exec orchestrator curl http://news-service:8002/health
```

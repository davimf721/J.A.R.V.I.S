# JARVIS API - Guia Completo

## 📚 Índice

1. [Endpoints Principais](#endpoints-principais)
2. [Autenticação](#autenticação)
3. [Fluxo de Podcast](#fluxo-de-podcast)
4. [Exemplos de Uso](#exemplos-de-uso)
5. [Tratamento de Erros](#tratamento-de-erros)
6. [Rate Limiting](#rate-limiting)
7. [Webhooks](#webhooks)

---

## 🔗 Endpoints Principais

### Orchestrator (Principal)

Base URL: `http://localhost:8010`

#### 1. Gerar Podcast

```
POST /api/podcast/generate
```

**Requisição:**
```json
{
  "id": "podcast_20260213_001",
  "agent_name": "JARVIS",
  "agent_type": "news_anchor",
  "language": "pt-BR",
  "podcast_duration_minutes": 8,
  "category": "general",
  "news_sources": ["bbc", "cnn", "techcrunch"]
}
```

**Resposta (202 - Accepted):**
```json
{
  "job_id": "podcast_20260213_001",
  "status": "pending",
  "message": "Podcast em fila de processamento",
  "estimated_completion_time_seconds": 120
}
```

**Parâmetros:**
| Campo | Tipo | Obrigatório | Padrão | Descrição |
|-------|------|-------------|--------|-----------|
| id | string | ✅ | - | Identificador único para o job |
| agent_name | string | ✅ | - | Nome do agente/podcaster |
| agent_type | string | ❌ | news_anchor | Tipo de agente |
| language | string | ❌ | pt-BR | Idioma do podcast |
| podcast_duration_minutes | number | ❌ | 8 | Duração em minutos |
| category | string | ❌ | general | Categoria de notícias |
| news_sources | array | ❌ | [] | Fontes de notícias |
| voice | string | ❌ | pt-BR-FranciscaNeural | Voz para TTS |
| skip_cache | boolean | ❌ | false | Ignorar cache |

---

#### 2. Verificar Status do Podcast

```
GET /api/podcast/status/{job_id}
```

**Resposta:**
```json
{
  "job_id": "podcast_20260213_001",
  "status": "processing",
  "created_at": "2026-02-13T10:30:00Z",
  "current_step": "generating_script",
  "progress": 45,
  "steps": {
    "fetch_news": {
      "status": "completed",
      "duration_seconds": 2.5,
      "output": {
        "news_count": 8,
        "total_news_items": 12
      }
    },
    "fetch_memory": {
      "status": "completed",
      "duration_seconds": 1.2
    },
    "generate_script": {
      "status": "processing",
      "duration_seconds": 15.3
    },
    "generate_audio": {
      "status": "pending"
    },
    "save_result": {
      "status": "pending"
    }
  }
}
```

**Possíveis Status:**
- `pending` - Aguardando processamento
- `processing` - Em processamento
- `completed` - Concluído com sucesso
- `failed` - Falha no processamento
- `cancelled` - Cancelado pelo usuário

---

#### 3. Obter Resultado Completo

```
GET /api/podcast/result/{job_id}
```

**Resposta (200 - Sucesso):**
```json
{
  "job_id": "podcast_20260213_001",
  "status": "completed",
  "result": {
    "script": "Olá, bem-vindo ao podcast JARVIS...",
    "audio_url": "s3://jarvis-media/podcasts/podcast_20260213_001.mp3",
    "audio_duration_seconds": 480,
    "news_items": 8,
    "word_count": 1245,
    "generated_at": "2026-02-13T10:32:15Z"
  }
}
```

---

#### 4. Listar Podcasts

```
GET /api/podcasts?limit=10&offset=0&status=completed
```

**Parâmetros Query:**
- `limit` (integer) - Quantos resultados retornar (padrão: 10, máximo: 100)
- `offset` (integer) - Paginar resultados (padrão: 0)
- `status` (string) - Filtrar por status (pending, processing, completed, failed)
- `agent_name` (string) - Filtrar por agente
- `from_date` (ISO-8601) - Podcasts após esta data
- `to_date` (ISO-8601) - Podcasts anteriores a esta data

**Resposta:**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "podcasts": [
    {
      "job_id": "podcast_001",
      "agent_name": "JARVIS",
      "status": "completed",
      "created_at": "2026-02-13T10:30:00Z",
      "duration_seconds": 480
    },
    {
      "job_id": "podcast_002",
      "agent_name": "JARVIS News",
      "status": "completed",
      "created_at": "2026-02-13T09:00:00Z",
      "duration_seconds": 520
    }
  ]
}
```

---

#### 5. Cancelar Podcast

```
POST /api/podcast/{job_id}/cancel
```

**Resposta:**
```json
{
  "job_id": "podcast_20260213_001",
  "status": "cancelled",
  "message": "Podcast foi cancelado com sucesso"
}
```

---

### LLM Service

Base URL: `http://localhost:8001`

#### Gerar Texto

```
POST /api/llm/generate
```

**Requisição:**
```json
{
  "prompt": "Crie um roteiro para um podcast sobre tecnologia",
  "context": "Contexto relevante aqui",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Resposta:**
```json
{
  "text": "Olá, bem-vindo ao nosso podcast...",
  "model": "kimi-k2.5:cloud",
  "generated_tokens": 450,
  "execution_time_seconds": 12.5
}
```

---

### News Service

Base URL: `http://localhost:8002`

#### Buscar Notícias

```
POST /api/news/fetch
```

**Requisição:**
```json
{
  "language": "pt-BR",
  "limit": 8,
  "categories": ["tech", "business"],
  "skip_cache": false
}
```

**Resposta:**
```json
{
  "news": [
    {
      "title": "Título da notícia",
      "summary": "Resumo...",
      "source": "BBC",
      "published_at": "2026-02-13T10:00:00Z",
      "url": "https://...",
      "category": "tech"
    }
  ],
  "total_count": 8,
  "language": "pt-BR",
  "source_count": 3
}
```

---

### TTS Service

Base URL: `http://localhost:8004`

#### Síntese de Voz

```
POST /api/tts/generate
```

**Requisição:**
```json
{
  "text": "Bem-vindo ao podcast JARVIS",
  "voice": "pt-BR-FranciscaNeural",
  "speed": 1.0,
  "pitch": 0.0,
  "format": "mp3"
}
```

**Resposta:**
```json
{
  "audio_url": "s3://jarvis-media/audio/audio_123456.mp3",
  "duration_seconds": 3.2,
  "format": "mp3",
  "file_size_bytes": 51200
}
```

---

### Memory Service

Base URL: `http://localhost:8005`

#### Armazenar Memória

```
POST /api/memory/store
```

**Requisição:**
```json
{
  "user_id": "user_123",
  "content": "Conteúdo a armazenar",
  "metadata": {
    "type": "podcast_script",
    "date": "2026-02-13",
    "podcast_id": "podcast_001"
  }
}
```

---

#### Buscar Memória Semântica

```
POST /api/memory/search
```

**Requisição:**
```json
{
  "user_id": "user_123",
  "query": "podcasts sobre tecnologia",
  "limit": 5,
  "threshold": 0.7
}
```

**Resposta:**
```json
{
  "results": [
    {
      "id": "mem_001",
      "content": "...",
      "similarity_score": 0.92,
      "metadata": {}
    }
  ]
}
```

---

## 🔐 Autenticação

Todos os endpoints exigem token JWT ou API Key (se `ENABLE_AUTH=true`).

### Login

```
POST /api/auth/login
```

**Requisição:**
```json
{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Usar Token

Adicionar header em todas as requisições:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Or use API Key:
```
X-API-Key: sua_chave_api
```

---

## 🎬 Fluxo de Podcast

```
1. POST /api/podcast/generate
   ↓
2. Job criado com status "pending"
   ↓
3. Sistema inicia pipeline:
   a) GET /api/news/fetch → Busca notícias
   b) POST /api/memory/search → Recupera contexto
   c) POST /api/llm/generate → Gera roteiro
   d) POST /api/tts/generate → Gera áudio
   e) PUT /api/podcast/{id}/complete → Salva resultado
   ↓
4. GET /api/podcast/status/{id} → Verificar progresso
   ↓
5. GET /api/podcast/result/{id} → Obter resultado final
```

---

## 💻 Exemplos de Uso

### Bash/cURL

```bash
# 1. Gerar podcast
curl -X POST http://localhost:8010/api/podcast/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu_token" \
  -d '{
    "id": "podcast_bash_001",
    "agent_name": "JARVIS",
    "agent_type": "news_anchor",
    "language": "pt-BR"
  }'

# 2. Verificar status (repetir até completed)
curl http://localhost:8010/api/podcast/status/podcast_bash_001 \
  -H "Authorization: Bearer seu_token"

# 3. Obter resultado
curl http://localhost:8010/api/podcast/result/podcast_bash_001 \
  -H "Authorization: Bearer seu_token"

# 4. Listar últimos podcasts
curl "http://localhost:8010/api/podcasts?limit=10&status=completed" \
  -H "Authorization: Bearer seu_token"
```

### Python

```python
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8010"
API_KEY = "seu_token"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 1. Crear podcast
response = requests.post(
    f"{BASE_URL}/api/podcast/generate",
    headers=headers,
    json={
        "id": "podcast_python_001",
        "agent_name": "JARVIS Python",
        "agent_type": "storyteller",
        "language": "pt-BR",
        "podcast_duration_minutes": 10
    }
)

if response.status_code == 202:
    job_id = response.json()["job_id"]
    print(f"Job criado: {job_id}")
    
    # 2. Monitorar progresso
    while True:
        status_response = requests.get(
            f"{BASE_URL}/api/podcast/status/{job_id}",
            headers=headers
        )
        
        status_data = status_response.json()
        status = status_data.get("status")
        progress = status_data.get("progress", 0)
        
        print(f"Status: {status} ({progress}%)")
        
        if status == "completed":
            # 3. Obter resultado
            result_response = requests.get(
                f"{BASE_URL}/api/podcast/result/{job_id}",
                headers=headers
            )
            result = result_response.json()
            print(f"Podcast concluído!")
            print(f"Audio URL: {result['result']['audio_url']}")
            break
        elif status == "failed":
            print("Podcast falhou!")
            break
        
        sleep(5)
else:
    print(f"Erro: {response.status_code}")
    print(response.json())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8010';
const API_KEY = 'seu_token';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_KEY}`
};

async function generatePodcast() {
  try {
    // 1. Gerar podcast
    const generateResponse = await axios.post(
      `${BASE_URL}/api/podcast/generate`,
      {
        id: 'podcast_nodejs_001',
        agent_name: 'JARVIS NodeJS',
        agent_type: 'analyst',
        language: 'pt-BR'
      },
      { headers }
    );

    const jobId = generateResponse.data.job_id;
    console.log(`Job criado: ${jobId}`);

    // 2. Monitorar status
    let completed = false;
    while (!completed) {
      const statusResponse = await axios.get(
        `${BASE_URL}/api/podcast/status/${jobId}`,
        { headers }
      );

      const { status, progress } = statusResponse.data;
      console.log(`Status: ${status} (${progress}%)`);

      if (status === 'completed') {
        // 3. Obter resultado
        const resultResponse = await axios.get(
          `${BASE_URL}/api/podcast/result/${jobId}`,
          { headers }
        );

        console.log('Podcast concluído!');
        console.log(resultResponse.data.result);
        completed = true;
      } else if (status === 'failed') {
        console.error('Podcast falhou!');
        completed = true;
      } else {
        // Aguardar 5 segundos antes de verificar novamente
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  } catch (error) {
    console.error('Erro:', error.response?.data || error.message);
  }
}

generatePodcast();
```

---

## ⚠️ Tratamento de Erros

### Códigos HTTP

| Código | Significado | Ação |
|--------|-------------|------|
| 200 | OK | Requisição sucedida |
| 202 | Accepted | Job aceito e enfileirado |
| 400 | Bad Request | Parâmetros inválidos |
| 401 | Unauthorized | Token inválido ou faltando |
| 402 | Payment Required | Limite de quota atingido |
| 404 | Not Found | Recurso não encontrado |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Server Error | Erro interno |
| 503 | Service Unavailable | Serviço indisponível |

### Exemplo de Erro

```json
{
  "error": "invalid_request",
  "message": "Campo 'agent_name' é obrigatório",
  "code": 400,
  "request_id": "req_123456",
  "timestamp": "2026-02-13T10:30:00Z"
}
```

---

## 🚦 Rate Limiting

Se `ENABLE_RATE_LIMITING=true`:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1676281200
```

Limite padrão: 100 requisições por minuto por usuário.

---

## 🪝 Webhooks (Futuro)

Configure webhooks para receber notificações quando um podcast for concluído:

```bash
POST /api/webhooks/subscribe

{
  "event": "podcast.completed",
  "url": "https://seu-servidor.com/webhook",
  "retry_strategy": "exponential"
}
```

---

## 📊 Métricas

Acesso às métricas Prometheus:
```
http://localhost:9090/graph
```

Métricas úteis:
- `jarvis_podcast_total` - Número total de podcasts gerados
- `jarvis_podcast_duration_seconds` - Tempo de processamento
- `jarvis_llm_requests_total` - Número de chamadas ao LLM
- `jarvis_cache_hits_total` - Acertos de cache

---

## 📞 Suporte

Para problemas:

1. Verifique logs:
   ```bash
   docker-compose logs orchestrator
   ```

2. Teste endpoint de saúde:
   ```bash
   curl http://localhost:8010/health
   ```

3. Veja documentação em:
   ```
   http://localhost:8010/docs (Swagger)
   http://localhost:8010/redoc (ReDoc)
   ```


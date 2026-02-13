# JARVIS - Guia Completo de Inicialização e Uso

## 🚀 Início Rápido para macOS

### 1. Executar Script de Setup

```bash
# Torne o script executável
chmod +x setup-mac.sh

# Execute o script (requer macOS)
./setup-mac.sh
```

**O que o script faz:**
- ✅ Verifica macOS
- ✅ Instala Xcode Command Line Tools (se necessário)
- ✅ Instala Homebrew (se necessário)
- ✅ Instala Docker Desktop (se necessário)
- ✅ Inicia Docker
- ✅ Cria arquivo `.env`
- ✅ Constrói imagens Docker
- ✅ Inicia todos os contêineres
- ✅ Aguarda todos os serviços ficarem prontos
- ✅ Mostra instruções de uso

**Tempo esperado:** 10-30 minutos (primeira vez)

---

## 📝 Configurações Obrigatórias

Após o setup, verifique o arquivo `.env`:

```bash
nano .env
```

Configurações importantes:

```env
# Modelo LLM (mude conforme disponível)
OLLAMA_MODEL=kimi-k2.5:cloud

# Credenciais (recomendado mudar em produção)
POSTGRES_PASSWORD=jarvis_secure_password
REDIS_PASSWORD=
RABBITMQ_PASSWORD=jarvis_queue_pwd
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

---

## 🎙️ Gerando Seu Primeiro Podcast

### Opção 1: CLI Interativa (Recomendado)

```bash
# Torne executável
chmod +x run-podcast.sh

# Execute
./run-podcast.sh
```

Escolha a opção 1 para "Gerar Podcast com Notícias" e siga as prompts.

### Opção 2: API REST

```bash
# Terminal 1: Monitorar logs
docker-compose logs -f orchestrator

# Terminal 2: Enviar requisição
curl -X POST http://localhost:8010/api/podcast/generate \
  -H "Content-Type: application/json" \
  -d '{
    "id": "meu_podcast_001",
    "agent_name": "JARVIS",
    "agent_type": "news_anchor",
    "language": "pt-BR",
    "podcast_duration_minutes": 8
  }'
```

**Resposta esperada:**
```json
{
  "job_id": "meu_podcast_001",
  "status": "pending",
  "message": "Podcast em fila de processamento"
}
```

### Opção 3: Python Script

```python
import requests
import json

api_url = "http://localhost:8010/api/podcast/generate"

payload = {
    "id": "python_podcast_001",
    "agent_name": "JARVIS AI",
    "agent_type": "storyteller",
    "language": "pt-BR",
    "podcast_duration_minutes": 10
}

response = requests.post(api_url, json=payload)
print(json.dumps(response.json(), indent=2))
```

---

## 📊 Monitorando Podcasts

### Ver Status em Tempo Real

**Via CLI:**
```bash
./run-podcast.sh
# Escolha opção 4: "[4] Ver Status do Último Podcast"
```

**Via API:**
```bash
curl http://localhost:8010/api/podcast/status/meu_podcast_001
```

**Resposta:**
```json
{
  "status": "processing",  // pending, processing, completed, failed
  "job_id": "meu_podcast_001",
  "request": {...},
  "created_at": "2026-02-13T10:30:00",
  "current_step": "generating_script",
  "progress": 45
}
```

### Ver Logs dos Serviços

```bash
# Todos os logs
docker-compose logs -f

# Um serviço específico
docker-compose logs -f llm-service
docker-compose logs -f script-service
docker-compose logs -f tts-service

# Últimas N linhas
docker-compose logs --tail=100 orchestrator
```

---

## 🔧 Gerenciamento de Contêineres

### Status

```bash
docker-compose ps
```

### Parar Serviços

```bash
# Parar mantendo dados
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose down -v
```

### Reiniciar Serviço Específico

```bash
docker-compose restart llm-service
docker-compose restart tts-service
docker-compose restart postgresql
```

### Executar Comando no Container

```bash
# Entrar no container
docker-compose exec llm-service bash

# Executar comando
docker-compose exec postgres psql -U jarvis -d jarvis_db
```

### Ver Recursos

```bash
docker stats
```

---

## 🤖 Tipos de Agentes

Você pode customize o tipo de agente para diferentes estilos de podcast:

| Tipo | Descrição | Tom |
|------|-----------|-----|
| `news_anchor` | Âncora de notícias profissional | Formal, informativo |
| `storyteller` | Contador de histórias | Narrativo, envolvente |
| `analyst` | Analista técnico | Profundo, analítico |
| `casual` | Conversa casual | Descontraído, amigável |

Exemplo:
```bash
curl -X POST http://localhost:8010/api/podcast/generate \
  -d '{
    "id": "podcast_storyteller",
    "agent_name": "JARVIS Storyteller",
    "agent_type": "storyteller",
    "language": "pt-BR"
  }'
```

---

## 🗣️ Modelos de Voz

Configure diferentes vozes para seus podcasts:

Vozes em Português (Azure):
- `pt-BR-FranciscaNeural` - Feminina, neutra (padrão)
- `pt-BR-AntonioNeural` - Masculina, neutra

Configurar na requisição:
```json
{
  "id": "podcast_antonio",
  "agent_name": "JARVIS",
  "voice": "pt-BR-AntonioNeural",
  "language": "pt-BR"
}
```

---

## 📚 Modelos LLM Disponíveis

Instalar modelos via Ollama:

```bash
# Conectar ao ollama
docker-compose exec ollama ollama list

# Instalar novo modelo
docker-compose exec ollama ollama pull mistral

# Usar novo modelo (editar .env)
OLLAMA_MODEL=mistral:latest
docker-compose restart llm-service
```

Modelos recomendados:
- `kimi-k2.5:cloud` - Excelente qualidade (padrão)
- `mistral:latest` - Rápido, bom custo-benefício
- `neural-chat:latest` - Conversacional
- `llama2:latest` - Popular, versátil

---

## 🔗 Dashboards e Ferramentas

Acesse as seguintes URLs no navegador:

| Ferramenta | URL | Credenciais |
|-----------|-----|-------------|
| **Grafana** (Métricas) | http://localhost:3000 | admin / admin |
| **Prometheus** (Queries) | http://localhost:9090 | - |
| **RabbitMQ** (Filas) | http://localhost:15672 | jarvis / jarvis_queue_pwd |
| **MinIO** (Storage) | http://localhost:9001 | minioadmin / minioadmin |
| **pgAdmin** (DB) | Não configurado (opcional) | - |

---

## 🐛 Resolução de Problemas

### Docker Não Inicia

```bash
# Verificar se Docker está rodando
docker info

# Se não estiver, abra Docker Desktop
open -a Docker

# Aguarde 30 segundos e tente novamente
```

### Serviços Não Ficam Prontos

```bash
# Ver logs
docker-compose logs ollama
docker-compose logs postgres

# Limpar e recomeçar
docker-compose down -v
./setup-mac.sh
```

### Espaço em Disco Cheio

```bash
# Limpar imagens não usadas
docker system prune -a

# Limpar volumes
docker volume prune

# Ver tamanho
du -sh ~/.Docker/Volumes/
```

### Memory Service (ChromaDB) Lento

```bash
# Reiniciar
docker-compose restart memory-service

# Verificar saúde
curl http://localhost:8200/api/v1/heartbeat
```

### LLM Gerando Respostas Curtas

Edite `.env`:
```env
LLM_TIMEOUT=600  # Aumentar de 300 para 600 segundos
```

Reinicie:
```bash
docker-compose restart llm-service
```

---

## 🔐 Segurança (Produção)

Para ambiente de produção:

1. **Mude todas as senhas** em `.env`:
```env
POSTGRES_PASSWORD=sua_senha_forte_aqui
REDIS_PASSWORD=sua_senha_redis_forte
RABBITMQ_PASSWORD=sua_senha_rabbitmq_forte
SECRET_KEY=sua_chave_secreta_aleatoria_forte
S3_SECRET_KEY=sua_chave_s3_forte
```

2. **Desabilite autenticação fraca:**
```env
ENABLE_AUTH=true
ENABLE_RATE_LIMITING=true
```

3. **Use reverse proxy com HTTPS:**
```bash
# Exemplo com Nginx
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

4. **Backup de dados:**
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U jarvis jarvis_db > backup.sql

# Backup volumes
docker run --rm -v jarvis_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

---

## 📈 Métricas e Monitoramento

### Ver Métricas em Tempo Real

```bash
# CPU, memória, rede dos containers
docker stats

# Métricas detalhadas
docker-compose exec prometheus curl http://localhost:9090/api/v1/query?query=container_cpu_usage_seconds_total
```

### Criar Dashboard Grafana

1. Acesse http://localhost:3000
2. Login: admin / admin
3. Data Source: Prometheus (http://prometheus:9090)
4. Crie dashboard com métricas de seus containers

---

## 🛠️ Desenvolvimento e Debug

### Modo Debug

```bash
# Ver variáveis de ambiente
docker-compose exec llm-service env | grep
-i ollama

# Conhecer IP interno
docker-compose exec llm-service nslookup postgres

# Testar conectividade
docker-compose exec llm-service curl http://orchestrator:8010/health
```

### Modificar Código

```bash
# 1. Edite o arquivo
nano services/llm-service/main.py

# 2. Rebuilde imagem
docker-compose build llm-service

# 3. Reinicie serviço
docker-compose up -d llm-service

# 4. Acompanhe logs
docker-compose logs -f llm-service
```

### Python REPL

```bash
# Entrar em um container e usar Python
docker-compose exec llm-service python

# Dentro do Python
>>> import sys
>>> sys.path.insert(0, '/app')
>>> from shared.config import OLLAMA_URL
>>> print(OLLAMA_URL)
```

---

## 🎯 Workflow Recomendado Diário

```bash
# 1. Inicie os serviços (se não estiverem rodando)
docker-compose up -d

# 2. Verifique saúde
./run-podcast.sh
# Escolha opção 5: "Verificar Saúde dos Serviços"

# 3. Gere podcasts
./run-podcast.sh
# Escolha opção 1 ou 2

# 4. Monitore progresso
docker-compose logs -f orchestrator

# 5. Quando terminar
docker-compose down
```

---

## 🚀 Próximos Passos

- 📖 Leia [ARCHITECTURE_VISUAL.md](/Users/ghoul/Documents/J.A.R.V.I.S/ARCHITECTURE_VISUAL.md) para entender a arquitetura
- 🔌 Explore [API_GUIDE.md](#) para integrar em suas aplicações
- 🐳 Customize [docker-compose.yml](docker-compose.yml) para seus serviços
- 📊 Configure alertas no Grafana
- 🔐 Configure backup automático de dados

---

## 📞 Suporte

Se tiver problemas:

1. **Verifique logs:**
   ```bash
   docker-compose logs | grep ERROR
   ```

2. **Verifique conectividade:**
   ```bash
   curl http://localhost:8010/health
   ```

3. **Reinicie tudo:**
   ```bash
   docker-compose down -v
   ./setup-mac.sh
   ```

4. **Verifique documentação:**
   - [TROUBLESHOOTING.md](/Users/ghoul/Documents/J.A.R.V.I.S/TROUBLESHOOTING.md)
   - [README.md](/Users/ghoul/Documents/J.A.R.V.I.S/README.md)

---

## 🎉 Parabéns!

Você está pronto para começar! 🚀

Execute seus primeiros podcasts e aproveite o poder do JARVIS!

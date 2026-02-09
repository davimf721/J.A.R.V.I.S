# JARVIS - Guia de Troubleshooting e Diagnóstico

## 📊 Resumo dos Scripts Disponíveis

### `start.ps1` - Script Principal
```powershell
# Iniciar serviços
.\start.ps1 start

# Iniciar com limpeza de cache Docker
.\start.ps1 start -Prune

# Parar serviços
.\start.ps1 stop

# Ver status
.\start.ps1 status

# Ver logs em tempo real
.\start.ps1 logs

# Limpar Docker
.\start.ps1 prune
```

### `diagnose.ps1` - Script de Diagnóstico
```powershell
# Executar diagnóstico completo
.\diagnose.ps1

# Executar com verbose (mais detalhes)
.\diagnose.ps1 -Verbose
```

---

## 🔴 Problemas Comuns e Soluções

### 1. **Erro: hnswlib - "Unsupported compiler"**

**Sintoma:**
```
RuntimeError: Unsupported compiler -- at least C++11 support is needed!
[memory-service 4/6] RUN pip install --no-cache-dir -r requirements.txt
```

**Causa:**
O container `memory-service` não tem ferramentas de compilação C++.

**✅ Solução:**
Já corrigido! O arquivo `services/memory-service/Dockerfile` agora inclui:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    gcc \
    && rm -rf /var/lib/apt/lists/*
```

**Teste:**
```powershell
.\start.ps1 start -Prune
```

---

### 2. **Erro: Transferência de contexto muito lenta (news-service, tts-service)**

**Sintoma:**
```
=> [news-service internal] load build context          1813.2s
 => => transferring context: 242.72MB                                                         1812.8s
```

**Causa:**
Arquivos desnecessários sendo copiados (podcasts/, __pycache__, etc)

**✅ Solução:**
Adicionado `.dockerignore` na raiz do projeto que exclus:
- `podcasts/` (dados de teste)
- `__pycache__/` (cache compilado)
- `.git/` (repositório)
- Arquivos de log e temporários

**Resultado esperado:**
Transferência deve ser <1 segundo agora.

---

### 3. **Erro: "ImportError" ou "ModuleNotFoundError"**

**Sintoma:**
```
from shared.config import X
ModuleNotFoundError: No module named 'shared'
```

**Causa:**
Path do Python não inclui shared/

**✅ Solução:**
Código já tem:
```python
sys.path.insert(0, os.path.dirname(__file__) + '/../../')
# ou
sys.path.insert(0, '/shared')  # in Docker
```

Se ainda tiver problema:
```powershell
docker logs jarvis-[service]  # Ver logs completos
.\diagnose.ps1 -Verbose       # Ver diagnóstico detalhado
```

---

### 4. **Erro: Serviço não responde no health check**

**Sintoma:**
```
[WARN] news-service não respondeu após 60 segundos
[DEBUG] Verifique os logs com: docker logs jarvis-news-service
```

**Causa:**
- Serviço ainda está iniciando
- Dependência não está pronta
- Erro na aplicação

**✅ Solução:**

**Opção 1: Aumentar timeout**
```powershell
# O script aguarda até 60 segundos, se precisar mais:
docker-compose ps  # Ver status dos containers
```

**Opção 2: Ver logs**
```powershell
docker logs jarvis-news-service
docker-compose logs news-service
```

**Opção 3: Verificar dependências**
```powershell
# Verificar se postgres/redis estão prontos
docker logs jarvis-postgres
docker logs jarvis-redis
```

---

### 5. **Porta já está em uso**

**Sintoma:**
```
Error response from daemon: Ports are not available: exposing port UDP 5432/tcp -> 0.0.0.0:5432: 
listen tcp 0.0.0.0:5432: bind: An attempt was made to use a port that was not available.
```

**Causa:**
Outra aplicação ou container anterior usando a porta.

**✅ Solução:**
```powershell
# Listar containers rodando
docker ps -a

# Parar e remover containers
docker-compose down -v

# Ou forçar remover
docker-compose down --remove-orphans -v

# Tentar iniciar novamente
.\start.ps1 start

# Se ainda tiver problema, limpar tudo
.\start.ps1 start -Prune
```

---

### 6. **Sem espaço em disco**

**Sintoma:**
```
[WARN] Espaço em disco baixo: 8.5GB livre de 256GB total
```

**Causa:**
Não há espaço suficiente para compilar containers + dados.

**✅ Solução:**
```powershell
# Verificar uso
docker system df

# Limpar imagens/containers não usados
.\start.ps1 prune
# ou manualmente
docker system prune -a --volumes

# Liberar espaço (delete files não essenciais)
# - podcasts/ pode ser deletado (são testes)
# - .git pode ser otimizado
```

**Requisitos minimos:**
- 20GB livres antes de iniciar
- 3.5-5.5GB durante build

---

### 7. **Erro: "depends_on condition not met"**

**Sintoma:**
```
service "postgres" required by "orchestrator" is not running
```

**Causa:**
Serviço dependente falhou ou não completou health check.

**✅ Solução:**
```powershell
# Ver status de todos os services
.\start.ps1 status

# Ver logs do serviço que falhou
docker logs jarvis-postgres

# Pode forçar aguardar:
docker-compose up -d --wait

# Ou iniciar com rebuild
docker-compose up -d --build
```

---

## 🔍 Como Diagnosticar Problemas

### 1. Executar diagnóstico completo
```powershell
.\diagnose.ps1 -Verbose
```

Isso informará:
- ✅ Versão do Docker
- ✅ Imagens disponíveis
- ✅ Containers rodando
- ✅ Espaço em disco
- ✅ Portas abertas
- ✅ Problemas detectados

### 2. Ver logs em tempo real
```powershell
# Todos os serviços
docker-compose logs -f --tail=100

# Serviço específico
docker-compose logs -f llm-service
docker logs -f jarvis-llm-service

# Com filtro
docker-compose logs -f 2>&1 | Select-String "ERROR"
```

### 3. Executar comandos dentro de um container
```powershell
# Entrar no container
docker exec -it jarvis-llm-service bash

# Ou verificar imports específicos
docker exec jarvis-llm-service python -c "from shared.config import OLLAMA_URL"
```

### 4. Reconstruir um serviço específico
```powershell
docker-compose up -d --build llm-service
```

---

## 📈 Informações de Logging do start.ps1

O script agora mostra:

```
[00:00:15] [INFO] Verificando Docker...
[00:00:15] [OK] Docker encontrado: Docker version 26.1.0, build d260a54
[00:00:16] [INFO] Verificando instalação do Docker...
[00:00:17] [OK] Docker daemon está ativo
[00:00:35] [DEBUG] - llm-service (porta 8001)
[00:01:02] [DEBUG] Servic ainda não está pronto - Tentativa 5/30
[00:01:05] [OK] llm-service está HEALTHY
```

**Componentes:**
- `[HH:MM:SS]` - Tempo decorrido desde o início
- `[INFO/OK/WARN/ERROR/DEBUG]` - Nível de severidade
- Mensagens descritivas para cada etapa

---

## 🚀 Performance Tips

### 1. Primeira inicialização
```powershell
# Pode levar 10-30 minutos
# Network é o gargalo (download de imagens)
.\start.ps1 start
```

### 2. Inicializações subsequentes
```powershell
# Muito mais rápido (usa cache)
.\start.ps1 start

# Se tiver mudanças no código:
docker-compose up -d --build

# Se tiver mudanças nas dependências:
docker-compose up -d --build --no-cache
```

### 3. Economizar espaço
```powershell
# Remover images antigas
docker image prune -a

# Remover volumes não usados
docker volume prune

# Limpeza completa
.\start.ps1 start -Prune
```

---

## 🔗 Portas Mapeadas

| Serviço | Porta | URL |
|---------|-------|-----|
| LLM Service | 8001 | http://localhost:8001 |
| News Service | 8002 | http://localhost:8002 |
| Script Service | 8003 | http://localhost:8003 |
| TTS Service | 8004 | http://localhost:8004 |
| Memory Service | 8005 | http://localhost:8005 |
| Orchestrator | 8010 | http://localhost:8010 |
| Ollama | 11435 | http://localhost:11435 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| RabbitMQ | 5672 | localhost:5672 |
| ChromaDB | 8200 | http://localhost:8200 |
| MinIO | 9000 | http://localhost:9000 |

---

## 📝 Logs Importantes

### Onde encontrar logs:
```powershell
# Docker compose
docker-compose logs [serviço]

# Arquivo de logs (se houver)
Get-ChildItem -Path ./services/*/logs/ -Recurse
```

### O que procurar:
- `ERROR` - Falhas críticas
- `WARN` - Avisos (pode continuar)
- `INFO` - Informações gerais
- `DEBUG` - Detalhes (se verbose)

---

## ✅ Checklist de Initialização

- [ ] Docker instalado e rodando
- [ ] 20GB+ de espaço livre no disco
- [ ] Portas 8001-8010 e infra disponíveis
- [ ] `.\start.ps1 start` executado com sucesso
- [ ] Todos os serviços em status `healthy` (GREEN)
- [ ] `.\start.ps1 status` mostrando todas as portas abertas

---

## 🆘 Se Nada Funcionar

```powershell
# Reset completo
docker-compose down -v --remove-orphans
Remove-Item -Path ./podcasts -Recurse -Force -ErrorAction SilentlyContinue
.\start.ps1 start -Prune

# Depois
.\diagnose.ps1 -Verbose

# E procure pelos erros na saída
```

Boa sorte! 🚀

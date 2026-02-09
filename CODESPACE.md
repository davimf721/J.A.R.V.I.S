# Inicialização - Codespace vs Windows Local

## 🚀 GitHub Codespace (Recomendado - Sem Espaco Local)

### Comando Único:
```bash
docker-compose up -d --build
```

### OU com script assistido:
```bash
chmod +x init-codespace.sh
./init-codespace.sh
```

**Tempo esperado:** 5-10 minutos

---

## 🖥️ Windows Local (Quando Tiver 20GB+ Livres)

### Opção 1: Script Automatizado (Recomendado)

Abra PowerShell como Administrador e execute:

```powershell
.\init-windows.ps1
```

O script vai:
- ✓ Validar Docker e docker-compose
- ✓ Verificar espaço em disco
- ✓ Parar containers antigos
- ✓ Executar `docker-compose up -d --build`
- ✓ Verificar saúde dos serviços
- ✓ Mostrar próximos passos

### Opção 2: Comando Direto

```powershell
docker-compose up -d --build
```

**Tempo esperado:** 10-30 minutos (primeira vez), 2-5 minutos (subsequentes)

## Monitorar Inicialização (Codespace ou Windows)

```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f llm-service
```

## Testar Serviços

```bash
# LLM Service
curl http://localhost:8001/health

# News Service
curl http://localhost:8002/health

# Orchestrator
curl http://localhost:8010/health
```

## Parar Tudo

```bash
docker-compose down
```

## Ver Logs de um Serviço

```bash
docker-compose logs -f llm-service
docker-compose logs -f memory-service
docker-compose logs -f orchestrator
```

## Endereços dos Serviços

| Serviço | URL | Porta |
|---------|-----|-------|
| LLM Service | http://localhost:8001 | 8001 |
| News Service | http://localhost:8002 | 8002 |
| Script Service | http://localhost:8003 | 8003 |
| TTS Service | http://localhost:8004 | 8004 |
| Memory Service | http://localhost:8005 | 8005 |
| Orchestrator | http://localhost:8010 | 8010 |
| Ollama | http://localhost:11435 | 11435 |

## Resetar Tudo

```bash
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

## Problemas Comuns

### Porta em uso
```bash
docker ps   # Ver containers rodando
docker kill <container_id>
```

### Erro ao compilar
```bash
docker-compose logs     # Ver todos os logs
docker-compose restart  # Reiniciar
```

### Limpar espaço em disco
```bash
docker system prune -a
docker image prune -a
```

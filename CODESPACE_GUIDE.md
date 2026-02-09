# GitHub Codespace - Guia Passo-a-Passo

## 1. Criar um Codespace

### Pré-requisito
- Conta GitHub

### Passos
1. Abra seu repositório no GitHub
2. Click em **Code** (botão verde)
3. Escolha a aba **Codespaces**
4. Click em **Create codespace on main**
5. Aguarde ~1-2 minutos para o ambiente inicializar

### Você vai ver
Ambiente VS Code rodando dentro do navegador com:
- Editor de código
- Terminal integrado
- Git integrado

---

## 2. Inicializar os Serviços

No terminal do Codespace (Ctrl+`):

### Opção A - Comando Direto (Mais Rápido)
```bash
docker-compose up -d --build
```

### Opção B - Script Assistido
```bash
chmod +x init-codespace.sh
./init-codespace.sh
```

**Aguarde:** 5-10 minutos para compilação

---

## 3. Acompanhar Progresso

Abra **novo terminal** (Ctrl+` ou `+` icon):

```bash
docker-compose logs -f
```

Você vai ver:
```
llm-service    | INFO: Creating application
news-service   | Starting Uvicorn server
memory-service | Initializing ChromaDB
...
```

Quando começar a repetir "health check passed" = sistema pronto!

---

## 4. Verificar Status

```bash
docker-compose ps
```

Esperado:
```
NAME                  STATUS
llm-service           Up 2 minutes
news-service          Up 2 minutes
memory-service        Up 2 minutes
orchestrator          Up 2 minutes
postgres              Up 2 minutes
redis                 Up 2 minutes
ollama                Up 3 minutes
```

---

## 5. Testar um Serviço

```bash
curl http://localhost:8001/health
```

Esperado:
```json
{
  "status": "healthy",
  "timestamp": "2025-02-09T10:30:00Z"
}
```

---

## 6. Ver Logs de um Serviço Específico

```bash
# LLM Service
docker-compose logs -f llm-service

# News Service
docker-compose logs -f news-service

# Orchestrator
docker-compose logs -f orchestrator

# Ollama (pode levar tempo para iniciar)
docker-compose logs -f ollama
```

---

## 7. Parar os Serviços

```bash
docker-compose down
```

Isto **não remove dados** (volumes persistem).

---

## 8. Reiniciar

```bash
docker-compose up -d
```

Muito mais rápido (segundos) pois já está compilado.

---

## Acessar Endereços

Dentro do Codespace, os serviços rodamlocalmente:

- LLM Service: `http://localhost:8001`
- News Service: `http://localhost:8002`
- Script Service: `http://localhost:8003`
- TTS Service: `http://localhost:8004`
- Memory Service: `http://localhost:8005`
- Orchestrator: `http://localhost:8010`

Você pode usar `curl` ou fazer requests via code.

---

## Debugar Problemas

### Build falhou?
```bash
docker-compose logs    # Ver todas as mensagens
docker-compose build   # Tentar rebuild
```

### Serviço não inicia?
```bash
docker-compose logs -f [nome-servico]
docker-compose restart [nome-servico]
```

### Porta em conflito?
```bash
docker ps              # Ver containers
docker kill [id]       # Parar container problemático
docker-compose up -d   # Tentar novamente
```

### Limpar tudo e recomeçar?
```bash
docker-compose down -v     # Remove containers e volumes
docker system prune -a      # Limpa imagens
docker-compose up -d --build  # Build fresh
```

---

## Dicas

1. **Não feche abas sem necessidade** - Mantém os logs visíveis
2. **Use múltiplos terminais** - Um para logs, outro para comandos
3. **Codespacestem 60h gratuitas/mês** - Suficiente para desenvolvimento
4. **Pode dormir o Codespace** - Dados persistem (volumes)
5. **Commit frequentemente** - Git integrado está ali

---

## Próximas Etapas

Após os serviços estarem rodando:

1. **Testar um endpoint:**
   ```bash
   curl -X GET http://localhost:8010/health
   ```

2. **Enviar uma requisição:**
   ```bash
   curl -X POST http://localhost:8010/run \
     -H "Content-Type: application/json" \
     -d '{"action": "fetch_news"}'
   ```

3. **Desenvolver e testar:**
   - Modifique arquivos no Codespace
   - Build automaticamente com watchdog
   - Teste no terminal

---

## Custos

**Codespace é GRÁTIS** com limites:
- 60 horas/mês (conta gratuita)
- Máquinas 2-core padrão
- Perfeito para desenvolvimento

Se exceder, cobra ~$0.18/hora

## Quando Usar Cada Um

| Situação | Usar |
|----------|------|
| Prototipagem rápida | Codespace ✅ |
| Sem espaço local | Codespace ✅ |
| Desenvolvimento extenso | Windows Local |
| CI/CD testing | Codespace ✅ |
| Produção | Servidor dedicado |

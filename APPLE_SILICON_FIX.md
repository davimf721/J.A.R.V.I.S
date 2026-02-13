# 🍎 JARVIS - Troubleshooting para Apple Silicon (M1/M2/M3)

**Se você encontrar erros de Docker ao executar `./setup-mac.sh`, siga este guia.**

---

## ❌ Erro: "Platform mismatch - linux/amd64 vs linux/arm64"

Este erro significa que uma imagem Docker foi construída para Intel e você está em Apple Silicon.

### ✅ Solução Rápida

```bash
# 1. Parar tudo
docker-compose down

# 2. Limpar imagens antigas
docker system prune -a

# 3. Executar setup novamente
./setup-mac.sh
```

---

## ❌ Erro: "dependency failed to start: container jarvis-redis exited (1)"

Redis estava recebendo um comando inválido.

### ✅ Solução Rápida

```bash
# Limpar e reiniciar
docker-compose down
docker system prune -a
./setup-mac.sh
```

---

## ❌ Erro: "ChromaDB" container fails to start

ChromaDB pode ter compatibilidade inconsistente com arm64.

### ✅ Solução

```bash
# Removemos imagem específica antiga
docker rmi ghcr.io/chroma-core/chroma:0.3.23 2>/dev/null || true

# Executar setup novamente (vai usar versão latest compatível)
./setup-mac.sh
```

---

## ✅ O Que Foi Corrigido

| Problema | Solução |
|----------|---------|
| ChromaDB arm64 | Atualizar para `ghcr.io/chroma-core/chroma:latest` com suporte arm64 |
| Redis requirepass | Remover comando requirepass vazio que causava erro |
| docker-compose | Melhorar tratamento de erros e limpeza de containers antigos |
| Diagnóstico | Adicionar função `diagnose_arm64()` para detectar problemas |

---

## 🔍 Como Verificar que Funcionou

Após executar `./setup-mac.sh`, você deve ver:

```
✓ Arquitetura: Apple Silicon (M1/M2/M3)
✓ Apple Silicon (arm64) detectado
✓ Docker suporta linux/arm64
✓ Espaço em disco OK
✓ [14 contêineres criados e rodando]
```

---

## 🔧 Verificação Rápida de Status

```bash
# Ver status de todos os containers
docker-compose ps

# Deve mostrar: STATUS "Up X seconds" ou "Up X minutes"

# Se algum estiver "Exited", ver logs:
docker-compose logs <nome-do-container>

# Exemplo:
docker-compose logs chromadb
docker-compose logs redis
```

---

## 🚀 Próximo Passo

Após corrigir, execute:

```bash
./quick-podcast.sh
```

---

## 📞 Se Ainda Tiver Problemas

```bash
# Diagnóstico completo
docker system df
docker ps -a
docker-compose logs
docker-compose logs --tail=20 orchestrator

# Reset completo
docker-compose down -v
docker system prune -a
./setup-mac.sh
```

---

**Data:** 13 de fevereiro de 2026  
**Suporte:** Apple Silicon (arm64) ✅  
**Status:** Corrigido e testado

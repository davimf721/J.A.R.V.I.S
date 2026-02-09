# JARVIS - Quick Start

## 🎯 Escolha Seu Ambiente

### Sem Espaço Local? → GitHub Codespace ⭐ RECOMENDADO

```bash
docker-compose up -d --build
```

Pronto! Espere 5-10 minutos.

### Com 20GB+ Livres? → Windows Local

```powershell
.\init-windows.ps1
```

Pronto! Script faz tudo automaticamente.

---

## 📊 Comparação

| Aspecto | Codespace | Windows Local |
|---------|-----------|---------------|
| Espaço necessário | 0 (usa servidor GH) | 20GB+ |
| Setup | Automático | 5-10 min |
| Velocidade | Depende internet | Rápido |
| Custo | Gratuito (60h/mês) | Grátis |
| Ideal para | Teste rápido | Desenvolvimento |

---

## 🔧 Comandos Universais

```bash
# Ver status
docker-compose ps

# Ver logs tempo real
docker-compose logs -f

# Ver logs de um serviço
docker-compose logs -f llm-service

# Testar saúde
curl http://localhost:8001/health
curl http://localhost:8010/health

# Parar tudo
docker-compose down

# Resetar (remove dados!)
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

---

## ✅ Verificar Que Funcionou

Espere 5-10 minutos e execute:

```bash
docker-compose ps       # Todos devem estar "Up"
curl http://localhost:8001/health  # Deve retornar HTTP 200
```

Sucesso! 🎉

---

## 📚 Mais Informação

- `CODESPACE.md` - Detalhes de ambos
- `docker-compose.yml` - Configuração dos serviços
- `TROUBLESHOOTING.md` - Problemas comuns

# 🚀 Configuração do Groq para J.A.R.V.I.S

O **Groq** é uma API de LLM **gratuita** e extremamente **rápida** (até 500 tokens/segundo). 
Perfeito para demonstrações e apresentações a investidores!

## ⚡ Por que Groq?

| Característica | Groq | Ollama Local |
|----------------|------|--------------|
| **Velocidade** | ~500ms | 30-120s |
| **Custo** | Gratuito | Gratuito mas exige hardware |
| **Modelo** | Llama 3.3 70B | Limitado pela RAM |
| **Setup** | 2 minutos | 30+ minutos |

---

## 📋 Passo a Passo

### 1. Criar Conta no Groq (2 minutos)

1. Acesse: **https://console.groq.com**
2. Clique em **"Sign Up"** (login com Google/GitHub)
3. Acesse **"API Keys"** no menu lateral
4. Clique em **"Create API Key"**
5. **Copie a chave** (começa com `gsk_...`)

### 2. Configurar o Projeto

Crie um arquivo `.env` na raiz do projeto:

```bash
# Copiar o template
cp .env.example .env
```

Edite o `.env` e adicione sua API key:

```env
# LLM Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_SUA_API_KEY_AQUI
GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Iniciar o Projeto

```bash
# Iniciar todos os serviços (sem precisar do Ollama!)
docker compose up -d

# Verificar se está funcionando
curl http://localhost:8001/health
```

---

## 🧪 Testar a Geração

```bash
# Teste rápido
curl -X POST http://localhost:8001/api/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Crie uma introdução para um podcast sobre tecnologia"}'
```

**Resultado esperado:** Resposta em menos de 2 segundos! 🎉

---

## 📊 Modelos Disponíveis (Gratuitos)

| Modelo | Tokens/min | Ideal para |
|--------|------------|------------|
| `llama-3.3-70b-versatile` | 6,000 | **Recomendado** - Melhor qualidade |
| `llama-3.1-8b-instant` | 30,000 | Alta velocidade |
| `mixtral-8x7b-32768` | 5,000 | Contexto longo |
| `gemma2-9b-it` | 15,000 | Eficiente |

Para mudar o modelo, edite o `.env`:

```env
GROQ_MODEL=llama-3.1-8b-instant
```

---

## 🎯 Para Demonstrações

### Comandos úteis para apresentar:

```bash
# Gerar um podcast completo
curl -X POST http://localhost:8010/api/orchestrator/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "inteligência artificial", "duration_minutes": 5}'

# Ver status do sistema
curl http://localhost:8010/health

# Ver informações do LLM
curl http://localhost:8001/api/llm/info
```

---

## ⚠️ Limites do Plano Gratuito

- **Requests:** ~30/minuto (suficiente para demos)
- **Tokens:** ~6,000/minuto com Llama 3.3 70B
- **Sem restrições:** Uso comercial permitido

Para produção com alto volume, considere upgrade (~$0.05/1M tokens).

---

## 🔧 Troubleshooting

### "GROQ_API_KEY não configurada"
```bash
# Verificar se o .env está correto
cat .env | grep GROQ
```

### "Rate limit exceeded"
Aguarde 1 minuto ou mude para um modelo mais rápido:
```env
GROQ_MODEL=llama-3.1-8b-instant
```

### Voltar para Ollama (se necessário)
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
```

---

## 🎬 Pronto para Investidores!

Com Groq configurado, você terá:
- ✅ Respostas em **menos de 2 segundos**
- ✅ Modelo **Llama 3.3 70B** (estado da arte)
- ✅ **Zero custo** para demonstrações
- ✅ Sistema **profissional** e escalável

Boa sorte com os investidores! 🚀

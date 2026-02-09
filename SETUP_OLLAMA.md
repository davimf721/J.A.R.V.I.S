# 🚀 Guia: Iniciar Ollama e Testar Conexão

## 🔴 Problema Comum

```
Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket address
```

**Causa:** Há outro processo Ollama já rodando na porta 11434.

---

## ✅ Solução Rápida

### Opção 1: Usar o Script Automático (Recomendado)
```powershell
# Na pasta do projeto, execute:
cd C:\Users\tisuporte\Documents\jarvis_local

# Abra um terminal separado e execute:
.\start_ollama.bat
```

**O que faz:**
- ✅ Para qualquer Ollama que esteja rodando
- ✅ Aguarda a porta ficar disponível  
- ✅ Inicia um novo Ollama

### Opção 2: Parar Manualmente (PowerShell - Admin)

```powershell
# Listar processos Ollama
Get-Process ollama -ErrorAction SilentlyContinue

# Parar todos os processos
Stop-Process -Name ollama -Force

# Aguardar
Start-Sleep -Seconds 3

# Iniciar Ollama
ollama serve
```

### Opção 3: Parar Manualmente (CMD - Admin)

```cmd
taskkill /IM ollama.exe /F /T
timeout /t 3
ollama serve
```

---

## 🧪 Testar Conexão

Após iniciar Ollama, em outro terminal execute:

```powershell
cd C:\Users\tisuporte\Documents\jarvis_local\jarvis-core
python .\test_ollama.py
```

**Esperado:**
```
✅ Ollama está rodando!
✅ Modelos encontrados:
   🎯 qwen3:4b
✅ Conexão OK!
✅ TUDO OK! Ollama está pronto para usar
```

---

## 🔄 Workflow Completo

**Terminal 1 - Iniciar Ollama:**
```powershell
.\start_ollama.bat
```

**Terminal 2 - Testar (opcional):**
```powershell
cd jarvis-core
python .\test_ollama.py
```

**Terminal 3 - Executar JARVIS:**
```powershell
cd jarvis-core
python .\agent.py
```

---

## ❌ Troubleshooting

### Linux:
```bash
curl https://ollama.ai/install.sh | sh
```

## Passo 2: Baixar o Modelo Qwen3

```bash
ollama pull qwen3:4b
```

Isso pode levar alguns minutos dependendo da sua conexão.

## Passo 3: Verificar Instalação

Execute o diagnóstico:

```bash
cd jarvis_local/jarvis-core
python diagnose_ollama.py
```

Você deve ver:
```
✅ Ollama já está rodando!
✅ qwen3:4b
✅ Modelo 'qwen3:4b' funcionando!
✅ TUDO PRONTO! Ollama está funcionando corretamente!
```

## Passo 4: Iniciar JARVIS

### Opção A: Com Ollama em Background (Windows)

1. Duplo-clique em `start_ollama.bat`
   (Uma nova janela abrirá com Ollama rodando)

2. Em outra janela PowerShell:
```bash
cd jarvis-core
python agent.py
```

### Opção B: Com Ollama Manual (qualquer OS)

Terminal 1 (Ollama):
```bash
ollama serve
```

Terminal 2 (JARVIS):
```bash
cd jarvis-core
python agent.py'
```

## Troubleshooting

### Erro: "Modelo 'qwen3:4b' não encontrado"
```bash
ollama pull qwen3:4b
```

### Erro: "Não foi possível conectar ao Ollama"
Certifique-se que:
1. Ollama está rodando (`ollama serve`)
2. Porta 11434 está acessível
3. Não há firewall bloqueando

### Erro: "Read timed out"
- Seu modelo pode estar muito pesado
- Aumente o timeout em `config/settings.py`
- Ou use um modelo menor

### Fallback Automático

Se Ollama não estiver disponível, JARVIS usa:
- ✅ Modo MOCK automático
- ✅ Roteiro pré-definido para testes
- ✅ Sem erros ou travamentos

## Performance

| Modelo | Tamanho | RAM Mínimo | Tempo Resposta |
|--------|---------|-----------|-----------------|
| qwen3:4b | 2.5 GB | 4 GB | 30-60s |
| neural-chat:7b | 4 GB | 8 GB | 60-120s |

## Alternativas

Se Ollama não funcionar, use:

### OpenAI API
```python
OLLAMA_MODEL = "gpt-3.5-turbo"
USE_OPENAI = True
OPENAI_API_KEY = "sk-..."
```

### HuggingFace
```python
from transformers import pipeline
```

## Suporte

Para mais informações:
- Ollama: https://ollama.ai
- Qwen: https://github.com/QwenLM/Qwen
- JARVIS: Este projeto

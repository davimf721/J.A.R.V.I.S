import requests
import time
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from memory.memory import recall_memory
from utils.helpers import load_profile


def check_ollama_available():
    """Verifica se Ollama está disponível"""
    try:
        response = requests.get("http://localhost:11435/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False



def ask_llama(prompt: str) -> str:
    """
    Chama Ollama para gerar resposta.
    Sem fallback - lança erro se Ollama não estiver disponível.
    """
    # Carrega perfil do usuário
    profile = load_profile()

    # Recupera memórias relevantes
    memories = recall_memory(prompt)
    memory_context = "\n".join(memories) if memories else "Nenhuma memória relevante."

    # Prompt final enviado ao modelo
    full_prompt = f"""
PERFIL DO USUÁRIO:
{profile}

MEMÓRIAS IMPORTANTES:
{memory_context}

INSTRUÇÃO:
{prompt}
"""

    # Verificar se Ollama está disponível ANTES de tentar
    if not check_ollama_available():
        error_msg = """
❌ ERRO: Ollama não está disponível!

Para iniciar o Ollama, execute em outro terminal (PowerShell):
    $env:OLLAMA_HOST="127.0.0.1:11435" ; ollama serve

Ou execute o script de diagnóstico:
    python diagnose_ollama.py

Requisitos:
- Ollama deve estar rodando em http://localhost:11435
- Modelo '{OLLAMA_MODEL}' deve estar instalado
  (instale com: ollama pull {OLLAMA_MODEL})
""".format(OLLAMA_MODEL=OLLAMA_MODEL)
        raise RuntimeError(error_msg)

    try:
        print(f"\n🤖 [LLM] Conectando a Ollama ({OLLAMA_MODEL})...")
        print(f"   ⏳ Aguardando resposta (pode levar alguns minutos)...")
        
        # Chamada ao Ollama com timeout maior (300 segundos = 5 minutos)
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=300
        )

        # Verificar status
        if response.status_code == 404:
            error_msg = f"""
❌ ERRO: Modelo '{OLLAMA_MODEL}' não encontrado em Ollama!

Instale o modelo com:
    ollama pull {OLLAMA_MODEL}

Modelos disponíveis:
    ollama list
"""
            raise RuntimeError(error_msg)
        
        if response.status_code != 200:
            error_msg = f"""
❌ ERRO: Ollama retornou status {response.status_code}

Resposta: {response.text}
"""
            raise RuntimeError(error_msg)

        data = response.json()

        # Validação defensiva
        if "response" not in data:
            error_msg = f"""
❌ ERRO: Resposta inválida de Ollama

Dados recebidos: {data}
"""
            raise RuntimeError(error_msg)

        print(f"✅ Resposta recebida de Ollama!\n")
        return data["response"].strip()

    except requests.exceptions.Timeout:
        error_msg = f"""
❌ ERRO: Timeout ao conectar com Ollama (300s excedido)

Possíveis causas:
- Ollama está processando o modelo (processo muito lento)
- Sua máquina não tem recursos suficientes para rodar '{OLLAMA_MODEL}'
- Há problema com a rede ou Ollama travou

Recomendações:
1. Verifique a janela do Ollama - há alguma mensagem de erro?
2. Tente aumentar o timeout ou usar um modelo menor
3. Reinicie Ollama e tente novamente

Para reiniciar Ollama:
    Ctrl+C (na janela do Ollama)
    $env:OLLAMA_HOST="127.0.0.1:11435" ; ollama serve
"""
        raise RuntimeError(error_msg)
    
    except requests.exceptions.ConnectionError:
        error_msg = f"""
❌ ERRO: Não foi possível conectar ao Ollama em {OLLAMA_URL}

Para iniciar Ollama:
    $env:OLLAMA_HOST="127.0.0.1:11435" ; ollama serve

Confirme que Ollama está rodando:
    ollama list
"""
        raise RuntimeError(error_msg)
    
    except Exception as e:
        error_msg = f"""
❌ ERRO inesperado ao chamar Ollama

Tipo: {type(e).__name__}
Mensagem: {str(e)}

Verifique se Ollama está rodando corretamente:
    ollama serve
"""
        raise RuntimeError(error_msg) from e

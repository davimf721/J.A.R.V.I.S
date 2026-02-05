import requests
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from memory.memory import recall_memory
from utils.helpers import load_profile


def ask_llama(prompt: str) -> str:
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

    # Chamada ao Ollama
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        },
        timeout=120
    )

    # Segurança básica
    if response.status_code != 200:
        raise RuntimeError(
            f"Erro ao chamar Ollama ({response.status_code}): {response.text}"
        )

    data = response.json()

    # Validação defensiva (ESSENCIAL)
    if "response" not in data:
        raise RuntimeError(
            f"Ollama não retornou texto. Resposta completa: {data}"
        )

    return data["response"].strip()

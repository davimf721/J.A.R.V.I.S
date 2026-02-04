import requests
from config.settings import OLLAMA_URL, OLLAMA_MODEL
from memory.memory import recall_memory
from utils.helpers import load_profile

def ask_llama(prompt: str) -> str:
    profile = load_profile()
    memories = recall_memory(prompt)

    memory_context = "\n".join(memories)

    full_prompt = f"""
PERFIL DO USUÁRIO:
{profile}

MEMÓRIAS IMPORTANTES:
{memory_context}

INSTRUÇÃO:
{prompt}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
    )

    return response.json()["response"]

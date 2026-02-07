import json
import os
from tools.script_generator import generate_podcast_script
from utils.helpers import ask_for_feedback
from memory.memory import store_memory

OUTPUT_DIR = "output"

def run_jarvis():
    print("🤖 J.A.R.V.I.S online.")

    script = generate_podcast_script()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    roteiro_path = os.path.join(OUTPUT_DIR, "roteiro.txt")
    tts_request_path = os.path.join(OUTPUT_DIR, "tts_request.json")

    with open(roteiro_path, "w", encoding="utf-8") as f:
        f.write(script)

    # 🔥 Pedido de fala (contrato entre sistemas)
    with open(tts_request_path, "w", encoding="utf-8") as f:
        json.dump({
            "text": script,
            "voice": "default",
            "output": "podcast.wav"
        }, f, ensure_ascii=False, indent=2)

    feedback = ask_for_feedback()
    if feedback:
        store_memory(f"Feedback do usuário: {feedback}")

    print("🧠 Texto pronto. Voz será gerada por outro agente.")

if __name__ == "__main__":
    run_jarvis()

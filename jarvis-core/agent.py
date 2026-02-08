import json
import os
import subprocess
import sys
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

    print(f"\n✅ Roteiro gerado e salvo!")
    print(f"📄 Roteiro: {os.path.abspath(roteiro_path)}")
    print(f"📋 Requisição TTS: {os.path.abspath(tts_request_path)}")

    # Executar voice agent automaticamente
    print(f"\n🎙️ Iniciando geração de áudio...")
    try:
        voice_agent_path = os.path.join("..", "jarvis-voice", "voice_agent.py")
        result = subprocess.run(
            [sys.executable, voice_agent_path],
            cwd=os.path.dirname(__file__),
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print(f"\n🎵 Áudio gerado com sucesso!")
        else:
            print(f"\n⚠️  Voice agent retornou erro (código {result.returncode})")
    except FileNotFoundError:
        print(f"⚠️  Voice agent não encontrado em {voice_agent_path}")
        print(f"   Você pode executá-lo manualmente com: python ../jarvis-voice/voice_agent.py")
    except Exception as e:
        print(f"⚠️  Erro ao executar voice agent: {e}")

    # Feedback opcional
    feedback = ask_for_feedback()
    if feedback:
        store_memory(f"Feedback do usuário: {feedback}")

if __name__ == "__main__":
    run_jarvis()

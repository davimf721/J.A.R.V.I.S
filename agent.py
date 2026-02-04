from tools.script_generator import generate_podcast_script
from tools.tts import text_to_speech
from memory.memory import store_memory
from config.settings import OUTPUT_DIR
import os

def run_jarvis():
    print("🧠 J.A.R.V.I.S iniciando...")

    script = generate_podcast_script()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    roteiro_path = os.path.join(OUTPUT_DIR, "roteiro.txt")
    audio_path = os.path.join(OUTPUT_DIR, "podcast.wav")

    with open(roteiro_path, "w", encoding="utf-8") as f:
        f.write(script)

    text_to_speech(script, audio_path)

    store_memory("O usuário gosta de podcasts técnicos e objetivos sobre tecnologia.")

    print("🎙️ Podcast criado com sucesso.")
    print("🤖 J.A.R.V.I.S finalizou a tarefa.")

if __name__ == "__main__":
    run_jarvis()

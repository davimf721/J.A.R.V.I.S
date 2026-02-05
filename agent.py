from tools.script_generator import generate_podcast_script
from tools.tts import text_to_speech
from memory.memory import store_memory
from config.settings import OUTPUT_DIR
import os
from tools.speech_adapter import adapt_text_for_speech
from utils.helpers import ask_for_feedback


def run_jarvis():
    print("🤖 J.A.R.V.I.S online.")
    print("📡 Iniciando rotina de criação de podcast.")

    print("📰 Coletando notícias e gerando roteiro...")
    script = generate_podcast_script()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    roteiro_path = os.path.join(OUTPUT_DIR, "roteiro.txt")
    audio_path = os.path.join(OUTPUT_DIR, "podcast.wav")

    print("📝 Salvando roteiro em arquivo...")
    with open(roteiro_path, "w", encoding="utf-8") as f:
        f.write(script)

    print("🔊 Convertendo texto em áudio...")
    spoken_text = adapt_text_for_speech(script)
    text_to_speech(spoken_text, audio_path)

    print("🧠 Registrando preferência conhecida do usuário...")
    store_memory("O usuário gosta de podcasts técnicos e objetivos sobre tecnologia.")

    # 🆕 FEEDBACK
    feedback = ask_for_feedback()

    if feedback:
        memory_text = (
            f"Feedback do usuário sobre o podcast diário: {feedback}"
        )
        store_memory(memory_text)
        print("🧠 Feedback armazenado para aprendizado futuro.")

    print("\n✅ Tarefa concluída com sucesso.")
    print("🧠 J.A.R.V.I.S entrando em modo ocioso.")


if __name__ == "__main__":
    run_jarvis()

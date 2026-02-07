import os
import scipy.io.wavfile as wavfile
from pocket_tts import TTSModel

# Carregando o modelo uma vez
print("🧠 [TTS] Carregando Pocket-TTS model...")

# Carregue o modelo (pode demorar na primeira vez)
tts_model = TTSModel.load_model()

print("🧠 [TTS] Modelo carregado com sucesso.")

def text_to_speech(text: str, filename="podcast.wav"):
    # Garantir que o diretório exista
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Obter estado de voz (pode ser personalizado depois)
    voice_state = tts_model.get_state_for_audio_prompt("default")

    # Gerar áudio
    print("🔊 [TTS] Gerando áudio com Pocket-TTS...")
    audio = tts_model.generate_audio(voice_state, text)

    # Gravar em arquivo
    sample_rate = tts_model.sample_rate
    wavfile.write(filename, sample_rate, audio.numpy())

    print(f"🔊 [TTS] Áudio salvo em: {filename}")

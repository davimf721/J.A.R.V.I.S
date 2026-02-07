from pocket_tts import TTSModel
import soundfile as sf

print("🧠 [TTS] Carregando modelo...")
tts = TTSModel.load_model()

# estado persistente do modelo
state = {}

# ⚠️ texto como argumento POSICIONAL
out = tts._generate(
    "teste de voz do jarvis local",
    state
)

sf.write("teste.wav", out.audio, out.sample_rate)

print("Áudio gerado com sucesso")
print("Estado interno:", state.keys())

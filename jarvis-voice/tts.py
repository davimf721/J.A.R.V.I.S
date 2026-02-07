from pocket_tts import TTSModel
import soundfile as sf
import torch

print("🧠 [TTS] Carregando modelo...")
# Carrega o modelo com os parâmetros padrão
tts_model = TTSModel.load_model()

# Estado persistente (necessário para o modelo manter contexto se desejado)
# Para uma geração simples, podemos inicializar um estado vazio ou deixar o método lidar
_model_state: dict = {}

def text_to_speech(text: str, output_path: str):
    global _model_state
    
    # Se o estado estiver vazio, precisamos inicializá-lo adequadamente para o modelo
    # No pocket-tts, o estado geralmente é gerenciado internamente ou passado vazio
    # O método generate_audio espera o model_state.
    
    # ✅ USO CORRETO DO MÉTODO PÚBLICO
    # generate_audio retorna um torch.Tensor [samples]
    audio_tensor = tts_model.generate_audio(
        model_state=_model_state,
        text_to_generate=text
    )

    # Converter para numpy para salvar com soundfile
    audio_numpy = audio_tensor.cpu().numpy()

    sf.write(
        output_path,
        audio_numpy,
        tts_model.sample_rate
    )

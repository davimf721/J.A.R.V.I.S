import edge_tts
import asyncio
import traceback
from text_formatter import format_for_speech

print("🧠 [TTS] Inicializando TTS...")

# Vozes disponíveis para português brasileiro:
# - pt-BR-AntonioNeural (masculina - padrão, mais profissional)
# - pt-BR-FranciscaNeural (feminina - mais jovem/dinâmica)
# - pt-BR-ThalitaMultilingualNeural (feminina - multilíngue)
# - pt-PT-DuarteNeural (masculina - português de Portugal)
# - pt-PT-RaquelNeural (feminina - português de Portugal)

VOICE = "pt-BR-FranciscaNeural"  # Voz masculina natural
RATE = "+0%"  # Velocidade normal (pode ser +10%, -10%, etc)
PITCH = "+0Hz"  # Tom normal (pode ser +50Hz para mais agudo, -50Hz para mais grave)

async def generate_audio_async(text: str, output_path: str):
    """Gera áudio de forma assíncrona usando edge-tts"""
    try:
        # Formata o texto para ser mais natural
        formatted_text = format_for_speech(text)
        
        print(f"  🎬 [TTS] Gerando áudio ({len(formatted_text)} caracteres)...")
        
        communicate = edge_tts.Communicate(
            text=formatted_text,
            voice=VOICE,
            rate=RATE,
            pitch=PITCH
        )
        
        await communicate.save(output_path)
        print(f"  ✅ [TTS] Arquivo salvo com sucesso")
        
    except Exception as e:
        print(f"  ❌ [TTS] Erro na geração de áudio: {type(e).__name__}: {e}")
        print(f"  📋 [TTS] Stack trace:")
        traceback.print_exc()
        raise

def text_to_speech(text: str, output_path: str):
    """Interface síncrona para gerar TTS"""
    try:
        print(f"  📝 [TTS] Processando texto...")
        # Executar a função assíncrona
        asyncio.run(generate_audio_async(text, output_path))
        
    except Exception as e:
        print(f"  ❌ [TTS] Erro ao processar: {type(e).__name__}: {e}")
        raise

print("✅ [TTS] TTS inicializado com sucesso")

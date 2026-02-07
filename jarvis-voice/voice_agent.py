import json
import time
import os
from tts import text_to_speech

# Caminho relativo conforme a estrutura do seu projeto
REQUEST_FILE = "../jarvis-core/output/tts_request.json"

print("🔊 Jarvis Voice Agent online.")

while True:
    try:
        if os.path.exists(REQUEST_FILE):
            with open(REQUEST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            text = data["text"]
            output = data["output"]

            print(f"🎙️ Gerando áudio para: \"{text[:50]}...\"")
            text_to_speech(text, output)

            print(f"🔊 Áudio gerado com sucesso em: {output}")
            
            # Opcional: remover o arquivo de requisição após processar para não repetir
            # os.remove(REQUEST_FILE)
            
            break
        else:
            time.sleep(1)

    except Exception as e:
        print(f"❌ Erro ao processar: {e}")
        time.sleep(2)

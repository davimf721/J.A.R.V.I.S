import json
import time
import os
import traceback
import sys
from tts import text_to_speech
from text_formatter import format_for_speech

# Caminho relativo conforme a estrutura do seu projeto
REQUEST_FILE = "../jarvis-core/output/tts_request.json"

print("🔊 Jarvis Voice Agent online.")
print(f"📁 Aguardando requisições em: {os.path.abspath(REQUEST_FILE)}")
print("📝 Formatação automática de texto ATIVADA")

def process_request(file_path: str) -> bool:
    """
    Processa um arquivo de requisição JSON e gera áudio.
    Retorna True se processado com sucesso, False caso contrário.
    """
    try:
        # Ler o arquivo
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as je:
        print(f"  ❌ Erro ao decodificar JSON: {je}")
        return False
    except IOError as ie:
        print(f"  ❌ Erro ao ler arquivo: {ie}")
        return False

    # Validar campos obrigatórios
    text = data.get("text", "").strip()
    output = data.get("output", "").strip()
    
    if not text:
        print(f"  ❌ Campo 'text' vazio ou ausente")
        return False
        
    if not output:
        print(f"  ❌ Campo 'output' vazio ou ausente")
        return False
    
    # Log da requisição
    text_preview = text[:60] + "..." if len(text) > 60 else text
    print(f"  📋 Texto original: {text_preview}")
    print(f"  📁 Saída: {output}")
    
    # Formatar e exibir
    formatted = format_for_speech(text)
    print(f"\n✨ Texto formatado para fala:")
    print(f"  {formatted[:100]}..." if len(formatted) > 100 else f"  {formatted}")
    
    # Gerar áudio
    try:
        print(f"\n🎙️ Gerando áudio com formatação...")
        text_to_speech(text, output)
        print(f"\n✅ Processamento concluído!")
        print(f"🔊 Áudio salvo em: {os.path.abspath(output)}")
        return True
    except Exception as e:
        print(f"  ❌ Erro ao gerar áudio: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def main():
    """Loop principal do agente de voz"""
    attempt = 0
    
    while True:
        try:
            attempt += 1
            
            if os.path.exists(REQUEST_FILE):
                print(f"\n🔔 [Tentativa {attempt}] Arquivo de requisição encontrado")
                
                if process_request(REQUEST_FILE):
                    # Sucesso! Remover arquivo ou parar
                    print("\n💡 Dica: Descomente 'os.remove(REQUEST_FILE)' em voice_agent.py")
                    print("   para remover o arquivo após processar e evitar repetição.")
                    break
                else:
                    # Erro no processamento, tenta de novo
                    time.sleep(2)
            else:
                if attempt % 10 == 0:
                    print(f"⏳ Aguardando requisição... (tentativa {attempt})")
                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n⏸️  Agente pausado pelo usuário")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Erro inesperado: {type(e).__name__}: {e}")
            traceback.print_exc()
            time.sleep(2)


if __name__ == "__main__":
    main()

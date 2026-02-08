import asyncio
import edge_tts

async def list_voices():
    """Lista todas as vozes disponíveis do edge-tts"""
    voices = await edge_tts.list_voices()
    
    # Filtrar apenas vozes em português
    pt_voices = [v for v in voices if v['Locale'].startswith('pt')]
    
    print("=" * 80)
    print("VOZES DISPONÍVEIS EM PORTUGUÊS")
    print("=" * 80)
    
    for voice in pt_voices:
        print(f"\n🎤 {voice['ShortName']}")
        print(f"   Nome: {voice['FriendlyName']}")
        print(f"   Idioma: {voice['Locale']}")
        print(f"   Gênero: {voice['Gender']}")

asyncio.run(list_voices())

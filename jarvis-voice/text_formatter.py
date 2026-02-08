import re

def format_for_speech(text: str) -> str:
    """
    Formata o texto para ser mais natural ao falar.
    Remove ou transforma pontuações e elementos visuais que não fazem sentido em áudio.
    """
    
    # 1. Remover URLs
    text = re.sub(r'https?://[^\s]+', '', text)
    text = re.sub(r'www\.[^\s]+', '', text)
    
    # 2. Converter números em extenso (opcional - comentado por enquanto)
    # text = re.sub(r'\b(\d{4})\b', lambda m: num2words(m.group(1), lang='pt_BR'), text)
    
    # 3. Remover múltiplas pontuações (!!!, ???, etc)
    text = re.sub(r'([!?.])\1{2,}', r'\1', text)
    
    # 4. Espaço depois de pontuação (normalizar)
    text = re.sub(r'([.!?,;:])\s*', r'\1 ', text)
    
    # 5. Remover hífens múltiplos (---)
    text = re.sub(r'-{2,}', ' ', text)
    
    # 6. Remover asteriscos e outros símbolos usados para ênfase
    text = re.sub(r'[\*_`~]', '', text)
    
    # 7. Remover parênteses muito longos (comentários entre parênteses)
    text = re.sub(r'\([^)]{100,}\)', '', text)
    
    # 8. Limpar espaços em branco múltiplos
    text = re.sub(r'\s+', ' ', text)
    
    # 9. Converter algumas abreviações comuns
    replacements = {
        r'\bDr\.\s': 'Doutor ',
        r'\bDra\.\s': 'Doutora ',
        r'\bSr\.\s': 'Senhor ',
        r'\bSra\.\s': 'Senhora ',
        r'\bPL\s': 'Projeto de Lei ',
        r'\bCEP\b': 'CEP',
        r'\bCPF\b': 'CPF',
        r'\bCNPJ\b': 'CNPJ',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # 10. Remover quebras de linha múltiplas
    text = re.sub(r'\n{2,}', '\n', text)
    
    # 11. Transformar quebras de linha em pausa (ponto)
    text = text.replace('\n', '. ')
    
    # 12. Remover trailing punctuation e normalizar final
    text = text.rstrip()
    
    return text


def format_with_ssml(text: str, rate: str = "+0%", pitch: str = "+0Hz") -> str:
    """
    Formata o texto usando SSML (Speech Synthesis Markup Language) para melhor controle.
    Permite adicionar pausas, ênfase, e ajustes de tom.
    """
    
    # Primeiro, formata o texto base
    formatted = format_for_speech(text)
    
    # Envolver em tags SSML básicas
    ssml = f"""<speak>
    <voice name="pt-BR-AntonioNeural">
        <prosody rate="{rate}" pitch="{pitch}">
            {formatted}
        </prosody>
    </voice>
</speak>"""
    
    return ssml


if __name__ == "__main__":
    # Teste
    test_text = """
    E aí, Davi. Beleza??? Bora pro resumo técnico da sem...
    
    Essa semana foi INTENSA!!! lá no mundo da tecnologia. 
    Começando com a IA que não para de evoluir!!!
    
    https://exemplo.com/link-aleatorio está aqui.
    
    Você pode chamar Dr. Silva ou a Dra. Maria para mais info.
    
    Visite www.google.com para mais detalhes.
    """
    
    print("ORIGINAL:")
    print(test_text)
    print("\n" + "="*80 + "\n")
    print("FORMATADO:")
    print(format_for_speech(test_text))
    print("\n" + "="*80 + "\n")
    print("COM SSML:")
    print(format_with_ssml(test_text))

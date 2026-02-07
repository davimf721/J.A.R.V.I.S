import re

def adapt_text_for_speech(text: str) -> str:
    # Remove markdown e símbolos visuais
    text = re.sub(r"\*\*|\*|---", "", text)

    # Remove indicações entre parênteses
    text = re.sub(r"\(.*?\)", "", text)

    # Remove nomes de locutor
    text = re.sub(r"^[A-Za-z]+:\s*", "", text, flags=re.MULTILINE)

    # Quebras mais naturais
    text = text.replace("\n\n", ".\n")
    text = text.replace("\n", " ")

    return text.strip()

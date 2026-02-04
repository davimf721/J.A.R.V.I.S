from tools.news_fetcher import fetch_news
from llm.llama import ask_llama

def generate_podcast_script():
    news = fetch_news()

    news_text = "\n".join(
        f"- {n['title']}: {n['summary']}" for n in news
    )

    prompt = f"""
Crie um roteiro de podcast de tecnologia, fluido e bem explicado,
com cerca de 5 minutos de duração, baseado nas notícias abaixo:

{news_text}
"""

    return ask_llama(prompt)

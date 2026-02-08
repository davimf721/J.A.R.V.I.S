OLLAMA_URL = "http://localhost:11435/api/generate"  # Porta alternativa
OLLAMA_MODEL = "kimi-k2.5:cloud"  # Modelo local disponível

MEMORY_COLLECTION = "jarvis_memory"

# Configurações de memória
MEMORY_LIMIT = 0  # 0 = ilimitado, recupera TODAS as memórias relevantes

# Configurações de notícias
NEWS_LIMIT = 15  # Quantidade de notícias por fonte
NEWS_TOTAL_PER_PODCAST = 8  # Total de notícias diferentes a incluir no podcast

# Feeds de notícias - Tecnologia em português e inglês
NEWS_FEEDS = {
    # 🇧🇷 Português (Brasil)
    "DioLinux": "https://www.diolinux.com.br/feed",
    "Infowester": "https://www.infowester.com/feed/",
    
    # 🇺🇸 Inglês
    "ArsTechnica": "https://feeds.arstechnica.com/arstechnica/index",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Hacker News": "https://hnrss.org/frontpage",
    "TechCrunch": "http://feeds.techcrunch.com/techcrunch/startups",
    "GitHub Trending": "https://github.com/trending/rss",
    "Dev.to": "https://dev.to/feed",
}

OUTPUT_DIR = "data/outputs"

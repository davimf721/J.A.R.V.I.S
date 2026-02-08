import feedparser
from config.settings import NEWS_LIMIT, NEWS_TOTAL_PER_PODCAST, NEWS_FEEDS
import random
from datetime import datetime, timedelta

def fetch_news():
    """
    Busca notícias de múltiplas fontes e retorna as mais recentes.
    """
    articles = []
    
    print("📰 [NEWS] Buscando notícias de múltiplas fontes...")
    
    for source_name, feed_url in NEWS_FEEDS.items():
        try:
            parsed = feedparser.parse(feed_url)
            source_articles = 0
            
            for entry in parsed.entries[:NEWS_LIMIT]:
                # Tentar extrair resumo (fallback para title se não houver summary)
                summary = entry.get('summary', entry.get('title', 'Sem descrição'))
                
                # Limpar HTML tags básicas do summary
                summary = summary.replace('<p>', '').replace('</p>', '')
                summary = summary.replace('<br>', ' ').replace('</br>', '')
                summary = summary[:200]  # Limitar a 200 caracteres
                
                articles.append({
                    "source": source_name,
                    "title": entry.get('title', 'Sem título'),
                    "summary": summary,
                    "link": entry.get('link', ''),
                    "published": entry.get('published', '')
                })
                source_articles += 1
            
            if source_articles > 0:
                print(f"  ✅ {source_name}: {source_articles} notícia(s)")
            else:
                print(f"  ⚠️  {source_name}: Nenhuma notícia recuperada")
                
        except Exception as e:
            print(f"  ❌ Erro ao buscar {source_name}: {type(e).__name__}")
    
    # Embaralhar e retornar apenas as mais relevantes
    random.shuffle(articles)
    selected = articles[:NEWS_TOTAL_PER_PODCAST]
    
    print(f"\n📊 Total: {len(selected)} notícia(s) selecionada(s) para o podcast\n")
    
    return selected

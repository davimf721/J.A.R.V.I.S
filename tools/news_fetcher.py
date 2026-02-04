import feedparser
from config.settings import NEWS_LIMIT

FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage"
]

def fetch_news():
    articles = []
    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:NEWS_LIMIT]:
            articles.append({
                "title": entry.title,
                "summary": entry.summary
            })
    return articles

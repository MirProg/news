import trafilatura
import requests
from urllib.parse import urlparse

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AIBrief/1.0"

def fetch_article_text(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ""
        text = trafilatura.extract(downloaded, include_links=False, include_images=False)
        return (text or "").strip()
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return ""

def fetch_all_texts(articles):
    for i, a in enumerate(articles):
        print(f"  [{i+1}/{len(articles)}] Fetching: {a['title'][:60]}...")
        a["full_text"] = fetch_article_text(a["url"])
    return articles

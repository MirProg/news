import feedparser
import requests
import re
from datetime import datetime, timezone
from dateutil import parser as dateparser
from src.config import RSS_FEEDS, ARTICLES_PER_FEED, NEWSAPI_ENABLED, NEWSAPI_KEY, MAX_TOTAL_ARTICLES

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsBrief/1.0"

def _extract_image(entry):
    img = ""
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            if m.get("url") and "image" in m.get("type", ""):
                img = m["url"]
                break
    if not img and hasattr(entry, "links"):
        for link in entry.links:
            if link.get("rel") == "enclosure" and "image" in link.get("type", ""):
                img = link.get("href", "")
                break
    if not img:
        summary = entry.get("summary", entry.get("description", ""))
        match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', summary)
        if match:
            img = match.group(1)
    return img

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:ARTICLES_PER_FEED]:
            published = None
            if hasattr(entry, "published"):
                try:
                    published = dateparser.parse(entry.published)
                except Exception:
                    published = datetime.now(timezone.utc)
            text = entry.get("summary", entry.get("description", ""))
            clean = re.sub(r"<[^>]+>", "", text).strip()
            entries.append({
                "title": entry.get("title", "Untitled"),
                "url": entry.get("link", ""),
                "summary_raw": clean,
                "image_url": _extract_image(entry),
                "published": published or datetime.now(timezone.utc),
            })
        return entries
    except Exception as e:
        print(f"  RSS error {url}: {e}")
        return []

def fetch_newsapi():
    if not NEWSAPI_ENABLED:
        return []
    url = ("https://newsapi.org/v2/top-headlines"
           f"?sources=reuters,associated-press,bbc-news"
           f"&pageSize={ARTICLES_PER_FEED}&apiKey={NEWSAPI_KEY}")
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        data = resp.json()
        entries = []
        for article in data.get("articles", []):
            published = None
            if article.get("publishedAt"):
                try:
                    published = dateparser.parse(article["publishedAt"])
                except Exception:
                    published = datetime.now(timezone.utc)
            entries.append({
                "title": article.get("title", "Untitled"),
                "url": article.get("url", ""),
                "summary_raw": article.get("description", ""),
                "image_url": article.get("urlToImage", ""),
                "published": published or datetime.now(timezone.utc),
                "source": article.get("source", {}).get("name", "NewsAPI"),
            })
        return entries
    except Exception as e:
        print(f"  NewsAPI error: {e}")
        return []

def fetch_all():
    articles = []
    seen_urls = set()

    for feed in RSS_FEEDS:
        print(f"Fetching RSS: {feed['url']}")
        for a in fetch_rss(feed["url"]):
            a["source"] = feed["source"]
            if a["url"] and a["url"] not in seen_urls:
                seen_urls.add(a["url"])
                articles.append(a)

    for a in fetch_newsapi():
        if a["url"] and a["url"] not in seen_urls:
            seen_urls.add(a["url"])
            articles.append(a)

    articles.sort(key=lambda x: x["published"], reverse=True)
    return articles[:MAX_TOTAL_ARTICLES]

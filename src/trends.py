"""Trend tracking across hourly runs.

Stores article title history to identify hot/recurring stories.
"""

import os
import json
from datetime import datetime, timezone
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREND_FILE = os.path.join(HERE, "data", "trends.json")
HISTORY_SIZE = 24  # keep 24 hours of history

def load_history():
    if not os.path.exists(TREND_FILE):
        return []
    try:
        with open(TREND_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    os.makedirs(os.path.dirname(TREND_FILE), exist_ok=True)
    with open(TREND_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-HISTORY_SIZE:], f)

def get_hot_stories(articles):
    """Return article titles sorted by 'heat' (stories appearing across multiple runs)."""
    history = load_history()

    current_titles = set()
    current_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:00")
    entry = {"time": current_tag, "titles": []}
    for a in articles:
        t = a.get("title", "").strip()
        if t:
            current_titles.add(t)
            entry["titles"].append(t)
    history.append(entry)
    save_history(history)

    title_count = Counter()
    for h in history:
        for t in h.get("titles", []):
            title_count[t] += 1

    hot = [(t, c) for t, c in title_count.most_common(20) if t in current_titles]
    return hot


def tag_articles(articles):
    """Tag articles with 'hot' / 'trending' / 'new'."""
    hot_titles = set(t for t, _ in get_hot_stories(articles))
    for a in articles:
        if a.get("title") in hot_titles:
            a["trend"] = "hot"
        else:
            a["trend"] = "new"
    return articles

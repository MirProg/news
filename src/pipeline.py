#!/usr/bin/env python3
"""
AIBrief pipeline:
1. Fetch articles from RSS feeds
2. Download full article text
3. Deduplicate (same stories from different sources)
4. Rewrite with AI (OpenAI/Anthropic) or local AI (transformers)
5. Multi-perspective reasoning (analyst / strategist / contrarian / prediction)
6. Extract keywords for SEO
7. Trend tracking across hourly runs
8. Generate executive briefing + trend analysis
9. Generate static HTML site

Runs 24/7 via GitHub Actions cron (every hour).
"""

import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from src.fetcher import fetch_all
from src.content_fetcher import fetch_all_texts
from src.dedup import deduplicate
from src.ai_writer import generate_all
from src.local_ai import summarize as local_summarize
from src.config import LOCAL_AI_ENABLED
from src.reasoning import analyze_all
from src.keywords import extract_keywords
from src.briefing import generate_briefing
from src.trends import tag_articles
from src.generator import generate
from src.config import MAX_DAILY_GENERATED, AI_ENABLED, MAX_TOTAL_ARTICLES

def main():
    print("=" * 60)
    print("AIBrief — Multi-Perspective AI & Tech News Pipeline")
    print("=" * 60)

    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)

    print("\n[1/9] Fetching RSS feeds...")
    articles = fetch_all()
    print(f"  Found {len(articles)} articles")

    if not articles:
        print("  No articles found. Skipping.")
        return

    print(f"\n[2/9] Fetching article images (top {MAX_DAILY_GENERATED})...")
    articles = fetch_all_texts(articles, max_articles=10)
    img_count = sum(1 for a in articles if a.get("image_url"))
    print(f"  Found {img_count} images")

    print(f"\n[3/9] Deduplicating semantically...")
    articles = deduplicate(articles)
    print(f"  {len(articles)} unique articles remaining")

    print(f"\n[4/9] Rewriting articles...")
    if LOCAL_AI_ENABLED:
        print(f"  Using local AI (transformers)...")
        for a in articles:
            a["ai_content"] = local_summarize(a.get("full_text", "")) or a.get("summary_raw", "")
    elif AI_ENABLED:
        print(f"  Using cloud AI ({MAX_DAILY_GENERATED} max)...")
        articles = generate_all(articles[:MAX_DAILY_GENERATED])
    else:
        print(f"  No AI — fetching full text for site content...")
        for a in articles:
            a["ai_content"] = a.get("full_text", "") or a.get("summary_raw", "")

    print(f"\n[5/9] Multi-perspective reasoning (analyst/strategist/contrarian/prediction)...")
    articles = analyze_all(articles)

    print(f"\n[6/9] Extracting keywords...")
    for a in articles:
        a["keywords"] = extract_keywords(f"{a['title']} {a.get('summary_raw', '')}", top_n=5)

    print(f"\n[7/9] Trend tracking across hourly runs...")
    articles = tag_articles(articles)
    hot_count = sum(1 for a in articles if a.get("trend") == "hot")
    print(f"  {hot_count} hot/trending stories identified")

    print(f"\n[8/9] Generating executive briefing & trend analysis...")
    briefing = generate_briefing(articles)
    if briefing:
        print("  Briefing generated")
    else:
        print("  Briefing skipped (no AI)")

    print(f"\n[9/9] Generating static site...")
    generate(articles, briefing_raw=briefing)

    print("\n" + "=" * 60)
    print(f"Done. {len(articles)} articles published.")
    print("=" * 60)

if __name__ == "__main__":
    main()

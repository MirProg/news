import os

SITE_NAME = "AIBrief"
SITE_URL = "https://your-site.com"
SITE_DESC = "Daily AI & tech industry news, curated and rewritten by AI."

ARTICLES_PER_FEED = 5
MAX_TOTAL_ARTICLES = 30
MAX_DAILY_GENERATED = 15

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
AI_ENABLED = bool(OPENAI_API_KEY or ANTHROPIC_API_KEY)

RSS_FEEDS = [
    # AI / ML / Tech news
    {"url": "https://www.artificialintelligence-news.com/feed/",          "source": "AI News"},
    {"url": "https://venturebeat.com/feed/",                             "source": "VentureBeat"},
    {"url": "https://techcrunch.com/feed/",                              "source": "TechCrunch"},
    {"url": "https://www.theverge.com/rss/index.xml",                    "source": "The Verge"},
    {"url": "https://www.wired.com/feed/rss",                            "source": "Wired"},
    {"url": "https://arstechnica.com/feed/",                             "source": "Ars Technica"},
    {"url": "https://www.technologyreview.com/feed/",                   "source": "MIT Tech Review"},
    {"url": "https://feeds.feedburner.com/oreilly/radar/feed",           "source": "O'Reilly Radar"},
    {"url": "https://blog.google/technology/ai/rss/",                   "source": "Google AI"},
    {"url": "https://openai.com/blog/rss/",                              "source": "OpenAI"},
    {"url": "https://news.ycombinator.com/rss",                          "source": "Hacker News"},
    {"url": "https://www.zdnet.com/news/rss.xml",                        "source": "ZDNet"},
    {"url": "https://www.cnbc.com/id/100727362/device/rss/rss.html",     "source": "CNBC Tech"},
    {"url": "https://www.reuters.com/technology/arc/outboundfeeds/rss/", "source": "Reuters Tech"},
]

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_ENABLED = bool(NEWSAPI_KEY)

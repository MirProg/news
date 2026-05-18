"""Article rewriting using configured AI provider (DeepSeek/OpenAI/Anthropic)."""

from src.ai_client import chat
from src.config import AI_ENABLED, MAX_DAILY_GENERATED

SYSTEM = """You are an academic research journalist. Rewrite the following news article in your own words.
Keep the factual accuracy intact but change the structure and phrasing completely.
Write in a clear, professional tone suitable for a tech audience.
Output ONLY the rewritten article body (3-5 paragraphs). No preamble, no commentary."""

def generate_article(title, full_text, summary_raw):
    if not AI_ENABLED:
        return summary_raw
    if not full_text or len(full_text) < 100:
        return summary_raw

    prompt = f"Title: {title}\n\nSource article:\n{full_text[:4000]}"
    try:
        return chat(SYSTEM, prompt, temperature=0.7, max_tokens=1000)
    except Exception as e:
        print(f"  AI writing failed: {e}")
        return summary_raw


def generate_all(articles):
    for i, a in enumerate(articles):
        if a.get("full_text"):
            print(f"  AI writing [{i+1}/{len(articles)}]: {a['title'][:60]}...")
            a["ai_content"] = generate_article(
                a["title"], a.get("full_text", ""), a.get("summary_raw", "")
            )
        else:
            a["ai_content"] = a.get("summary_raw", "")
    return articles

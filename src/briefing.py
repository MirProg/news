"""Executive briefing — AI-generated daily summary connecting top stories."""

from src.ai_client import chat
from src.config import AI_ENABLED

SYSTEM = """You are an AI industry analyst. Given the day's top AI/tech articles, produce:
1. An EXECUTIVE BRIEFING (3-5 bullet points) — the most important things to know today
2. A TREND ANALYSIS paragraph — what patterns or themes connect these stories
3. A "WHY IT MATTERS" takeaway

Keep each section concise. Output in plain text with clear section headers."""


def generate_briefing(articles):
    if not AI_ENABLED or not articles:
        return None

    top = articles[:10]
    titles = "\n".join(f"- {a['title']} ({a['source']})" for a in top)
    prompt = f"Today's top AI/tech stories:\n{titles}"

    try:
        return chat(SYSTEM, prompt, temperature=0.5, max_tokens=800)
    except Exception as e:
        print(f"  Briefing generation failed: {e}")
        return None

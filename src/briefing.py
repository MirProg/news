"""Generate executive briefing and trend analysis from articles."""

from src.config import AI_PROVIDER, AI_ENABLED, OPENAI_API_KEY, ANTHROPIC_API_KEY

BRIEFING_SYSTEM = """You are an AI industry analyst. Given the day's top AI/tech articles, produce:
1. An EXECUTIVE BRIEFING (3-5 bullet points) — the most important things to know today
2. A TREND ANALYSIS paragraph — what patterns or themes connect these stories
3. A "WHY IT MATTERS" takeaway

Keep each section concise. Output in plain text with clear section headers."""

def _call_openai(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": BRIEFING_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=800,
    )
    return resp.choices[0].message.content.strip()

def _call_anthropic(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model="claude-3-haiku-20240307",
        system=BRIEFING_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.5,
    )
    return resp.content[0].text.strip()

def generate_briefing(articles):
    if not AI_ENABLED or not articles:
        return None

    top = articles[:10]
    titles = "\n".join(f"- {a['title']} ({a['source']})" for a in top)
    prompt = f"Today's top AI/tech stories:\n{titles}"

    try:
        if AI_PROVIDER == "anthropic":
            return _call_anthropic(prompt)
        return _call_openai(prompt)
    except Exception as e:
        print(f"  Briefing generation failed: {e}")
        return None

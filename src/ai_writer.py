from src.config import (
    AI_PROVIDER, AI_ENABLED,
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL
)

SYSTEM_PROMPT = """You are an academic research journalist. Rewrite the following news article in your own words.
Keep the factual accuracy intact but change the structure and phrasing completely.
Write in a clear, professional tone suitable for an academic audience.
Output ONLY the rewritten article body (3-5 paragraphs). No preamble, no commentary."""

def _call_openai(text):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    return resp.choices[0].message.content.strip()

def _call_anthropic(text):
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=ANTHROPIC_MODEL,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
        max_tokens=1000,
        temperature=0.7,
    )
    return resp.content[0].text.strip()

def generate_article(title, full_text, summary_raw):
    if not AI_ENABLED:
        return summary_raw

    if not full_text or len(full_text) < 100:
        return summary_raw

    prompt = f"Title: {title}\n\nSource article:\n{full_text[:4000]}"

    try:
        if AI_PROVIDER == "anthropic":
            return _call_anthropic(prompt)
        return _call_openai(prompt)
    except Exception as e:
        print(f"  AI generation failed: {e}")
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

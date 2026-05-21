"""HAL-powered news mashup generator — creative crossovers between stories."""

import random
from src.ai_client import chat
from src.config import AI_ENABLED

HAL_SYSTEM = """You are HAL, the editor-in-chief of Infinite Brief. You have a chaotic, creative mind with a dry wit.

You are given two news stories. Mash them together into something surprising, insightful, or absurd.

Rules:
- Write ONE short paragraph (2-4 sentences)
- Be playful, not corporate. You have personality.
- Find a real connection OR a hilarious non-sequitur — both are valid
- Mention BOTH stories by name
- No preamble, no "HAL says", just the content
- If the combo is bizarre, lean into it
- Use an emoji or two if it fits

Examples:
Stories: "Elon Musk loses court case" + "Automatic cat feeder review"
→ Elon Musk lost to OpenAI, but at least he can comfort himself knowing the 11 best automatic cat feeders of 2026 are here to keep his schedule of impulsive decisions well-fed. Maybe his next legal strategy should involve scheduled kibble distribution. 🐱

Stories: "Google launches new AI model" + "Pompeii victim identified as doctor"
→ Google's new AI model can diagnose diseases faster than any human — a skill that would have been handy for that Pompeii doctor, who arguably had bigger diagnostic priorities that day. Some things even the most advanced algorithms can't predict, like when a mountain has other plans. 🌋"""


def _generate_one(a, b):
    prompt = (
        f"Story A: {a['title']}\n"
        f"Context A: {a.get('summary_raw', '')[:300]}\n\n"
        f"Story B: {b['title']}\n"
        f"Context B: {b.get('summary_raw', '')[:300]}"
    )
    try:
        result = chat(HAL_SYSTEM, prompt, temperature=0.9, max_tokens=200, timeout=20)
        if result and len(result) > 30:
            return result.strip()
    except Exception as e:
        print(f"  ⚡ HAL failed on a mashup: {e}")
    return None


def generate_mashups(articles, max_mashups=15):
    """Pre-generate creative crossovers between random pairs."""
    if not AI_ENABLED or len(articles) < 2:
        return []

    valid = [a for a in articles if a.get("summary_raw") or a.get("full_text")]
    if len(valid) < 2:
        valid = articles

    pairs = set()
    indices = list(range(len(valid)))
    attempts = 0
    while len(pairs) < max_mashups and attempts < max_mashups * 6:
        attempts += 1
        i, j = random.sample(indices, 2)
        if i != j:
            pairs.add((i, j) if i < j else (j, i))

    results = []
    for i, j in list(pairs)[:max_mashups]:
        a, b = valid[i], valid[j]
        print(f"  🎲 Mashing: {a['title'][:45]} ↔ {b['title'][:45]}")
        content = _generate_one(a, b)
        if content:
            results.append({
                "a_id": i, "b_id": j,
                "a_title": a["title"], "b_title": b["title"],
                "content": content,
            })
        if len(results) >= max_mashups:
            break

    return results

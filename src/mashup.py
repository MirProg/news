"""HAL-powered news mashup generator with TF-IDF smart pairing."""

import random
from src.ai_client import chat
from src.config import AI_ENABLED
from src.similarity import suggest_mashup_pairs

HAL_SYSTEM = """You are HAL, the editor-in-chief of Infinite Brief. You have a chaotic, creative mind with a dry wit.

You are given two news stories. Mash them together into something surprising, insightful, or absurd.

Rules:
- Write ONE short paragraph (2-4 sentences)
- Be playful, not corporate. You have personality.
- Find a real connection OR a hilarious non-sequitur — both are valid
- Mention BOTH stories by name
- No preamble, no "HAL says", just the content
- If the combo is bizarre, lean into it
- Use an emoji or two if it fits"""


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
    """Pre-generate creative crossovers using TF-IDF smart pairing."""
    if not AI_ENABLED or len(articles) < 2:
        return []

    valid = [a for a in articles if a.get("summary_raw") or a.get("full_text")]
    if len(valid) < 2:
        valid = articles

    # Use TF-IDF similarity to pick coherent + absurd pairs
    pairs = suggest_mashup_pairs(valid, count=max_mashups)

    # Fallback to random if TF-IDF fails
    if not pairs:
        indices = list(range(len(valid)))
        random.shuffle(indices)
        pairs = []
        for k in range(0, len(indices) - 1, 2):
            if len(pairs) >= max_mashups:
                break
            pairs.append((indices[k], indices[k + 1], 0.0))

    results = []
    for i, j, score in pairs:
        a, b = valid[i], valid[j]
        vibe = "coherent" if score > 0.15 else "absurd"
        print(f"  🎲 [{vibe} sim={score:.2f}] {a['title'][:35]} ↔ {b['title'][:35]}")
        content = _generate_one(a, b)
        if content:
            results.append({
                "a_id": a.get("id", i), "b_id": b.get("id", j),
                "a_title": a["title"], "b_title": b["title"],
                "a_source": a.get("source", ""), "b_source": b.get("source", ""),
                "content": content,
                "vibe": vibe,
                "similarity": round(score, 3),
            })
        if len(results) >= max_mashups:
            break

    return results

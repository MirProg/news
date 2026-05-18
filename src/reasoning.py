"""Multi-perspective reasoning — Analyst, Strategist, Contrarian, Prediction."""

import json
import re
from src.ai_client import chat
from src.config import AI_ENABLED

SYSTEM = """You are an AI news analyst. For the given article, produce a multi-perspective analysis in JSON format with exactly these keys:
{
  "analyst": "1-2 sentence objective summary of what happened",
  "strategist": "1-2 sentence industry/strategic implications",
  "contrarian": "1-2 sentence what's being overlooked or a counterpoint",
  "prediction": "1 sentence prediction of what happens next"
}
Output ONLY valid JSON. No preamble."""


def _parse_json(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
    return {}


def analyze_article(title, summary, source):
    if not AI_ENABLED:
        return _fallback(title, summary)

    prompt = f"Source: {source}\nTitle: {title}\nSummary: {summary[:500]}"
    try:
        raw = chat(SYSTEM, prompt, temperature=0.7, max_tokens=500)
        result = _parse_json(raw)
        if result.get("analyst"):
            return result
        return _fallback(title, summary)
    except Exception as e:
        print(f"  Reasoning failed for '{title[:40]}...': {e}")
        return _fallback(title, summary)


def _fallback(title, summary):
    text = summary or title
    return {
        "analyst": text[:200] + ("..." if len(text) > 200 else ""),
        "strategist": "Set DEEPSEEK_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY for AI analysis.",
        "contrarian": "AI analysis requires an API key.",
        "prediction": "Requires API key.",
    }


def analyze_all(articles):
    for i, a in enumerate(articles):
        print(f"  Reasoning [{i+1}/{len(articles)}]: {a['title'][:50]}...")
        a["reasoning"] = analyze_article(
            a.get("title", ""),
            a.get("summary_raw", "") or a.get("full_text", "")[:500],
            a.get("source", ""),
        )
    return articles

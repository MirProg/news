"""Multi-perspective reasoning engine for each article.

Generates 3 AI viewpoints + a prediction for every article:
  - Analyst: What happened, key facts
  - Strategist: Industry implications
  - Contrarian: What's being overlooked
  - Prediction: "What happens next"
"""

import json
import re
from src.config import AI_PROVIDER, AI_ENABLED, OPENAI_API_KEY, ANTHROPIC_API_KEY

REASONING_SYSTEM = """You are an AI news analyst. For the given article, produce a multi-perspective analysis in JSON format with exactly these keys:
{
  "analyst": "1-2 sentence objective summary of what happened",
  "strategist": "1-2 sentence industry/strategic implications",
  "contrarian": "1-2 sentence what's being overlooked or a counterpoint",
  "prediction": "1 sentence prediction of what happens next"
}
Output ONLY valid JSON. No preamble."""

def _call_openai(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": REASONING_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content

def _call_anthropic(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model="claude-3-haiku-20240307",
        system=REASONING_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7,
    )
    return resp.content[0].text

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
    """Analyze a single article and return {analyst, strategist, contrarian, prediction}."""
    if not AI_ENABLED:
        return _fallback_analysis(title, summary)

    prompt = f"Source: {source}\nTitle: {title}\nSummary: {summary[:500]}"

    try:
        if AI_PROVIDER == "anthropic":
            raw = _call_anthropic(prompt)
        else:
            raw = _call_openai(prompt)
        result = _parse_json(raw)
        if result.get("analyst"):
            return result
        return _fallback_analysis(title, summary)
    except Exception as e:
        print(f"  Reasoning failed for '{title[:40]}...': {e}")
        return _fallback_analysis(title, summary)


def _fallback_analysis(title, summary):
    """Fallback when AI is not available."""
    text = summary or title
    return {
        "analyst": text[:200] + ("..." if len(text) > 200 else ""),
        "strategist": "Industry analysis requires an API key (OpenAI or Anthropic).",
        "contrarian": "Enable AI in config to get multi-perspective analysis.",
        "prediction": "Prediction requires AI. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.",
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

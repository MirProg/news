"""Shared AI client — transparently routes to DeepSeek, OpenAI, or Anthropic."""

from src.config import (
    AI_PROVIDER, AI_ENABLED,
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
)

def _get_openai_client():
    from openai import OpenAI
    if AI_PROVIDER == "deepseek":
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    return OpenAI(api_key=OPENAI_API_KEY)

def _get_model():
    if AI_PROVIDER == "deepseek":
        return DEEPSEEK_MODEL
    if AI_PROVIDER == "openai":
        return OPENAI_MODEL
    return ""

def chat(system, user, temperature=0.7, max_tokens=1000, response_format=None):
    """Call the configured AI provider. Returns text response."""
    if not AI_ENABLED:
        return ""

    kwargs = dict(
        model=_get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if AI_PROVIDER == "deepseek":
        kwargs.pop("response_format", None)

    if AI_PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        kwargs.pop("response_format", None)
        resp = client.messages.create(
            model=ANTHROPIC_MODEL,
            system=system,
            messages=[{"role": "user", "content": user}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.content[0].text.strip()

    # OpenAI-compatible (includes DeepSeek)
    client = _get_openai_client()
    if response_format:
        kwargs["response_format"] = response_format
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content.strip()

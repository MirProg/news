"""Shared AI client — Google, DeepSeek, OpenAI, Anthropic."""

import os
from src.config import (
    AI_PROVIDER, AI_ENABLED,
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GOOGLE_API_KEY, GOOGLE_MODEL,
)


def chat(system, user, temperature=0.7, max_tokens=1000, timeout=15, **kwargs):
    if not AI_ENABLED:
        return ""
    if AI_PROVIDER == "none":
        return ""

    if AI_PROVIDER == "google":
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            GOOGLE_MODEL,
            system_instruction=system,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        resp = model.generate_content(user, request_options={"timeout": timeout})
        return resp.text.strip()

    if AI_PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, max_retries=0)
        resp = client.messages.create(
            model=ANTHROPIC_MODEL,
            system=system,
            messages=[{"role": "user", "content": user}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.content[0].text.strip()

    from openai import OpenAI, APITimeoutError, APIConnectionError
    model = DEEPSEEK_MODEL if AI_PROVIDER == "deepseek" else OPENAI_MODEL
    base_url = "https://api.deepseek.com" if AI_PROVIDER == "deepseek" else None
    key = DEEPSEEK_API_KEY if AI_PROVIDER == "deepseek" else OPENAI_API_KEY

    if not key:
        return ""

    client = OpenAI(api_key=key, base_url=base_url, timeout=timeout, max_retries=0)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except (APITimeoutError, APIConnectionError) as e:
        raise ConnectionError(str(e))

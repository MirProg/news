"""Optional local AI summarizer using Hugging Face transformers + PyTorch.

Requires: pip install transformers torch
Set LOCAL_AI=true env var to enable.
"""

import os
import re

ENABLED = os.getenv("LOCAL_AI", "").lower() in ("1", "true", "yes")
_MODEL = None
_TOKENIZER = None

def _load_model():
    global _MODEL, _TOKENIZER
    if _MODEL is not None:
        return True
    try:
        from transformers import pipeline, AutoTokenizer
        import torch
        _TOKENIZER = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        _MODEL = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            tokenizer=_TOKENIZER,
            device=0 if torch.cuda.is_available() else -1,
        )
        return True
    except ImportError:
        print("  Local AI: transformers/torch not installed. pip install transformers torch")
        return False
    except Exception as e:
        print(f"  Local AI model load failed: {e}")
        return False


def summarize(text, max_length=300, min_length=80):
    if not ENABLED or len(text) < 200:
        return text

    if not _load_model():
        return text

    try:
        text = text[:3000]
        result = _MODEL(text, max_length=max_length, min_length=min_length, do_sample=False)
        return result[0]["summary_text"].strip()
    except Exception as e:
        print(f"  Local AI summarize failed: {e}")
        return text

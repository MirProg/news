"""Keyword extraction for SEO / tagging."""

import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

_NLTK_DOWNLOADED = False

def _ensure_nltk():
    global _NLTK_DOWNLOADED
    if _NLTK_DOWNLOADED:
        return
    try:
        stopwords.words("english")
    except LookupError:
        import nltk
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt_tab", quiet=True)
    _NLTK_DOWNLOADED = True

STOPWORDS = set()

def _get_stopwords():
    global STOPWORDS
    if not STOPWORDS:
        _ensure_nltk()
        STOPWORDS = set(stopwords.words("english"))
    return STOPWORDS

def extract_keywords(text, top_n=5):
    if not text:
        return []

    text_lower = text.lower()
    text_lower = re.sub(r"[^a-z0-9\s+#]", " ", text_lower)

    tokens = text_lower.split()
    stop = _get_stopwords()
    filtered = [t for t in tokens if t not in stop and len(t) > 2]

    bigrams = []
    for i in range(len(filtered) - 1):
        bigrams.append(f"{filtered[i]} {filtered[i+1]}")

    all_terms = filtered + bigrams
    freq = Counter(all_terms)
    return [term for term, _ in freq.most_common(top_n)]

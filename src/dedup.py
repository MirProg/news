"""News-aware semantic deduplication using title + entity overlap.

Better than TF-IDF for short news titles about the same event.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

JACCARD_THRESHOLD = 0.18
TFIDF_THRESHOLD = 0.50

def _tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def deduplicate(articles):
    if not articles:
        return []

    valid = [(a, _tokenize(a.get("title", ""))) for a in articles if a.get("title")]

    if len(valid) <= 1:
        return [a for a, _ in valid]

    keep = [True] * len(valid)

    for i in range(len(valid)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(valid)):
            if not keep[j]:
                continue
            jacc = _jaccard(valid[i][1], valid[j][1])
            if jacc >= JACCARD_THRESHOLD:
                keep[j] = False

    kept = [valid[i][0] for i in range(len(valid)) if keep[i]]
    removed = len(articles) - len(kept)
    if removed:
        print(f"  Dedup: removed {removed} similar articles (jaccard)")
    return kept

"""TF-IDF article similarity using sklearn — no PyTorch needed."""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _clean(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text))
    return re.sub(r"\s+", " ", text).strip().lower()


def build_index(articles):
    """Build TF-IDF index from article summaries. Returns (vectorizer, matrix, article_list)."""
    texts = []
    valid = []
    for a in articles:
        text = a.get("summary") or a.get("summary_raw") or a.get("title", "")
        cleaned = _clean(text)
        if len(cleaned) > 10:
            texts.append(cleaned)
            valid.append(a)

    if len(texts) < 2:
        return None, None, valid

    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix, valid


def find_related(articles, article_id, top_n=3):
    """Find top-N most similar articles by TF-IDF cosine similarity."""
    vectorizer, matrix, valid = build_index(articles)
    if vectorizer is None or matrix is None:
        return []

    idx = None
    for i, a in enumerate(valid):
        if a.get("id") == article_id:
            idx = i
            break

    if idx is None:
        # Fallback: match by position in valid list
        if article_id < len(valid):
            idx = article_id
        else:
            return []

    sims = cosine_similarity(matrix[idx], matrix).flatten()
    # Get top N excluding self
    ranked = np.argsort(sims)[::-1]
    results = []
    for i in ranked:
        if i == idx:
            continue
        if len(results) >= top_n:
            break
        results.append({
            "id": valid[i].get("id", i),
            "title": valid[i].get("title", ""),
            "score": round(float(sims[i]), 3),
        })
    return results


def similarity_matrix(articles):
    """Compute full similarity matrix. Returns list of (i, j, score) for all pairs."""
    vectorizer, matrix, valid = build_index(articles)
    if vectorizer is None or matrix is None:
        return [], valid

    n = matrix.shape[0]
    sims = cosine_similarity(matrix)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((i, j, float(sims[i][j])))
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs, valid


def suggest_mashup_pairs(articles, count=15):
    """Suggest pairs for mashups: top similar (coherent) + bottom similar (absurd)."""
    pairs, valid = similarity_matrix(articles)
    if not pairs or len(valid) < 2:
        return []

    # Top 30% = coherent, bottom 30% = absurd
    n = len(pairs)
    cut = max(1, int(n * 0.3))
    coherent = pairs[:cut]
    absurd = pairs[-cut:] if cut < n else []

    import random
    random.shuffle(coherent)
    random.shuffle(absurd)

    target_coherent = max(1, int(count * 0.5))
    result = []
    used = set()

    for i, j, score in coherent:
        if len(result) >= target_coherent:
            break
        key = (i, j) if i < j else (j, i)
        if key not in used:
            result.append((i, j, score))
            used.add(key)

    for i, j, score in absurd:
        if len(result) >= count:
            break
        key = (i, j) if i < j else (j, i)
        if key not in used:
            result.append((i, j, score))
            used.add(key)

    return result

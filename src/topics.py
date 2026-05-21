"""Article topic clustering using sklearn TF-IDF + KMeans."""

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min


def _clean(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text))
    return re.sub(r"\s+", " ", text).strip().lower()


def _extract_topic_label(texts, vectorizer, cluster_center, top_n=4):
    """Generate a human-readable label for a cluster using top TF-IDF terms."""
    # Get feature names
    feature_names = vectorizer.get_feature_names_out()
    # Get top terms closest to cluster center
    center = cluster_center.toarray()[0]
    top_indices = center.argsort()[::-1][:top_n]
    return [feature_names[i] for i in top_indices]


def cluster_articles(articles, n_clusters=None):
    """Cluster articles by topic using TF-IDF + KMeans. Returns list with cluster_id and label."""
    texts = []
    valid = []
    for i, a in enumerate(articles):
        text = a.get("summary") or a.get("summary_raw") or a.get("title", "")
        cleaned = _clean(text)
        if len(cleaned) > 20:
            texts.append(cleaned)
            a["_idx"] = i
            valid.append(a)

    if len(texts) < 3:
        for a in valid:
            a["topic_id"] = 0
            a["topic_label"] = "General"
        return valid

    vectorizer = TfidfVectorizer(
        max_features=500,
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts)

    n = min(n_clusters or max(3, len(texts) // 5), len(texts))
    n = max(2, n)

    kmeans = KMeans(n_clusters=n, random_state=42, n_init=5)
    labels = kmeans.fit_predict(matrix)

    # Generate topic labels for each cluster
    cluster_labels = {}
    for cid in range(n):
        mask = labels == cid
        if mask.sum() == 0:
            cluster_labels[cid] = "General"
            continue
        center = kmeans.cluster_centers_[cid]
        # Get top words from cluster center
        feature_names = vectorizer.get_feature_names_out()
        top_idx = center.argsort()[::-1][:3]
        label = ", ".join(feature_names[idx] for idx in top_idx)
        cluster_labels[cid] = label.title()

    for a, label in zip(valid, labels):
        a["topic_id"] = int(label)
        a["topic_label"] = cluster_labels[int(label)]

    return valid

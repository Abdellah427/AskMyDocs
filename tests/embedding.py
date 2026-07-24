"""A deterministic, dependency-free embedding used by the tests.

It maps text to a bag-of-words vector over a fixed vocabulary. Documents that
share topic words end up close in vector space, which lets the retrieval and
rerank pipelines be exercised end to end without downloading a real model.
"""

import numpy as np

VOCAB = ["cat", "dog", "car", "tree", "music", "ocean"]


def embed(texts):
    """Embed a list of strings as bag-of-words count vectors."""
    vectors = []
    for text in texts:
        words = text.lower().split()
        vectors.append([float(words.count(term)) for term in VOCAB])
    return np.asarray(vectors, dtype="float32")


def build_corpus():
    """Return a small topic-labelled corpus and its embeddings."""
    docs = []
    for topic in VOCAB:
        docs.append(f"{topic} {topic} {topic} article")
        docs.append(f"a short note about {topic}")
    return docs, embed(docs)

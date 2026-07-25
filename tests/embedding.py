"""A deterministic, dependency-free embedding used by the tests.

Maps text to a bag-of-words vector over a fixed vocabulary so that documents
sharing topic words end up close, letting the retrieval pipeline run end to end
without downloading a real model.
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


def build_passages():
    """Return the corpus as Passage objects with a source filename."""
    from src.retrieval import Passage

    docs, embeddings = build_corpus()
    passages = [Passage(text=d, source="corpus.csv") for d in docs]
    return passages, embeddings


def keyword_cross_encoder(pairs):
    """Fake cross-encoder: score by word overlap between query and passage."""
    scores = []
    for query, passage in pairs:
        q = set(query.lower().split())
        p = set(passage.lower().split())
        scores.append(float(len(q & p)))
    return scores

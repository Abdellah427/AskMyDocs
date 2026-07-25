"""Tests for the recall@k evaluation helper."""

from src.eval import recall_at_k
from src.retrieval import RagIndex
from tests.embedding import build_passages, embed


def _index():
    passages, embeddings = build_passages()
    return RagIndex(passages, embeddings, embed)


def test_recall_at_k_perfect():
    idx = _index()
    questions = ["cat", "dog", "music"]
    expected = ["cat", "dog", "music"]
    assert recall_at_k(lambda q, k: idx.dense(q, k), questions, expected, k=3) == 1.0


def test_recall_at_k_miss():
    idx = _index()
    # Asking about cats never surfaces an ocean passage in the top-1.
    assert recall_at_k(lambda q, k: idx.dense(q, k), ["cat"], ["ocean"], k=1) == 0.0


def test_recall_at_k_empty():
    idx = _index()
    assert recall_at_k(lambda q, k: idx.dense(q, k), [], [], k=3) == 0.0

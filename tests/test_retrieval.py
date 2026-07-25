"""Tests for the retrieval core: dense, hybrid (BM25 + RRF) and rerank."""

import numpy as np

from src.retrieval import RagIndex, reciprocal_rank_fusion
from tests.embedding import build_passages, embed, keyword_cross_encoder


def _index():
    passages, embeddings = build_passages()
    return RagIndex(passages, embeddings, embed)


def test_reciprocal_rank_fusion_prefers_agreement():
    a = [(1, 0.9), (2, 0.5), (3, 0.1)]
    b = [(2, 0.8), (1, 0.7), (4, 0.2)]
    fused = reciprocal_rank_fusion([a, b])
    # Items 1 and 2 rank high in both lists, so they come first.
    assert {idx for idx, _ in fused[:2]} == {1, 2}


def test_dense_returns_matching_topic():
    idx = _index()
    results = idx.dense("tell me about the cat", k=1)
    assert len(results) == 1
    assert "cat" in results[0].text
    assert results[0].source == "corpus.csv"


def test_dense_respects_k():
    idx = _index()
    assert len(idx.dense("ocean waves", k=3)) == 3


def test_hybrid_returns_matching_topic():
    idx = _index()
    results = idx.hybrid("a question about music", k=2)
    assert len(results) == 2
    assert all("music" in p.text for p in results)


def test_rerank_orders_by_cross_encoder():
    idx = _index()
    results = idx.rerank("dog dog park", score_fn=keyword_cross_encoder, k=2)
    assert len(results) == 2
    assert all("dog" in p.text for p in results)
    # Scores are non-increasing after reranking.
    assert results[0].score >= results[1].score


def test_empty_corpus_is_safe():
    idx = RagIndex([], np.zeros((0, len(embed(["x"])[0])), dtype="float32"), embed)
    assert idx.dense("anything", k=3) == []
    assert idx.hybrid("anything", k=3) == []

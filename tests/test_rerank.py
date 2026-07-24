"""Round-trip test for the PCA + rerank pipeline (src/rerank.py)."""

from src.rerank import load_faiss, search_and_rerank
from tests.embedding import build_corpus, embed


def test_load_faiss_shapes():
    _docs, embeddings = build_corpus()
    index, pca = load_faiss(embeddings)

    # Every document is present in the index.
    assert index.ntotal == embeddings.shape[0]
    # PCA never outputs more dimensions than features or samples.
    assert pca.d_out <= min(embeddings.shape[0], embeddings.shape[1])


def test_search_and_rerank_ranks_matching_topic_first():
    docs, embeddings = build_corpus()
    index, pca = load_faiss(embeddings)

    results = search_and_rerank(pca, "a question about a cat", index, docs, embed_fn=embed, top_k=3)

    assert len(results) == 3
    # The best-ranked passage is about the queried topic.
    assert "cat" in results[0]
    # And it carries a relevance score.
    assert "Relevance:" in results[0]


def test_search_and_rerank_empty_corpus():
    _docs, embeddings = build_corpus()
    index, pca = load_faiss(embeddings)

    assert search_and_rerank(pca, "anything", index, [], embed_fn=embed, top_k=3) == []


def test_rerank_keeps_only_matching_topic_on_top():
    # After reranking, the top results for a topic query are the documents of
    # that topic, and unrelated topics are pushed out of the top-k.
    docs, embeddings = build_corpus()
    index, pca = load_faiss(embeddings)

    results = search_and_rerank(pca, "music please", index, docs, embed_fn=embed, top_k=2)

    assert len(results) == 2
    assert all("music" in passage for passage in results)
    assert all("Relevance:" in passage for passage in results)

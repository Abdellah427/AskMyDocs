"""Retrieval core: dense, sparse (BM25), hybrid fusion and cross-encoder rerank.

Deliberately free of any LangChain dependency. Everything that touches a model
is injected (``embed_fn``, ``score_fn``) so the logic is testable offline.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple

import faiss
import numpy as np


@dataclass
class Passage:
    """A retrievable chunk of text and where it came from."""

    text: str
    source: str = ""
    score: float = 0.0


def _normalize(matrix: np.ndarray) -> np.ndarray:
    """L2-normalize rows so inner product equals cosine similarity."""
    matrix = np.asarray(matrix, dtype="float32")
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / (norms + 1e-12)


def _tokenize(text: str) -> List[str]:
    """Lowercase word tokenizer used for BM25."""
    return [t for t in "".join(c if c.isalnum() else " " for c in text.lower()).split() if t]


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[Tuple[int, float]]], k: int = 60
) -> List[Tuple[int, float]]:
    """Fuse several ranked lists of ``(index, score)`` with Reciprocal Rank Fusion.

    RRF ignores raw scores and combines by rank, which makes dense and sparse
    scores (on different scales) safe to merge.
    """
    fused: dict = defaultdict(float)
    for ranking in rankings:
        for rank, (idx, _score) in enumerate(ranking):
            fused[idx] += 1.0 / (k + rank + 1)
    return sorted(fused.items(), key=lambda item: item[1], reverse=True)


class RagIndex:
    """Holds passages and their embeddings, and serves the three retrieval modes."""

    def __init__(
        self,
        passages: List[Passage],
        embeddings: np.ndarray,
        embed_fn: Callable[[List[str]], np.ndarray],
    ):
        self.passages = passages
        self.texts = [p.text for p in passages]
        self.embed_fn = embed_fn

        self.embeddings = _normalize(embeddings)
        self.dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(self.embeddings)

        self._corpus_tokens = [_tokenize(t) for t in self.texts]
        self._bm25 = None  # built lazily on first sparse query

    # -- internals ---------------------------------------------------------
    def _query_vector(self, query: str) -> np.ndarray:
        return _normalize(np.asarray(self.embed_fn([query]), dtype="float32"))

    def _dense_ranking(self, query: str, k: int) -> List[Tuple[int, float]]:
        k = min(k, len(self.texts))
        if k <= 0:
            return []
        scores, indices = self.index.search(self._query_vector(query), k)
        return [(int(i), float(s)) for i, s in zip(indices[0], scores[0]) if i != -1]

    def _bm25_ranking(self, query: str, k: int) -> List[Tuple[int, float]]:
        if not self._corpus_tokens:
            return []
        if self._bm25 is None:
            from rank_bm25 import BM25Okapi

            self._bm25 = BM25Okapi(self._corpus_tokens)
        scores = self._bm25.get_scores(_tokenize(query))
        order = np.argsort(scores)[::-1][:k]
        return [(int(i), float(scores[i])) for i in order]

    def _collect(self, ranked: Sequence[Tuple[int, float]]) -> List[Passage]:
        out = []
        for idx, score in ranked:
            p = self.passages[idx]
            out.append(Passage(text=p.text, source=p.source, score=round(float(score), 4)))
        return out

    # -- public retrieval modes -------------------------------------------
    def dense(self, query: str, k: int = 5) -> List[Passage]:
        """Pure vector search (cosine)."""
        return self._collect(self._dense_ranking(query, k))

    def hybrid(self, query: str, k: int = 5, recall: int = 20) -> List[Passage]:
        """Dense + BM25, fused with Reciprocal Rank Fusion."""
        if not self.texts:
            return []
        recall = min(recall, len(self.texts))
        dense = self._dense_ranking(query, recall)
        sparse = self._bm25_ranking(query, recall)
        fused = reciprocal_rank_fusion([dense, sparse])[:k]
        return self._collect(fused)

    def rerank(
        self,
        query: str,
        score_fn: Callable[[List[Tuple[str, str]]], Sequence[float]],
        k: int = 5,
        recall: int = 20,
    ) -> List[Passage]:
        """Hybrid recall, then re-order candidates with a cross-encoder.

        Args:
            score_fn: Maps ``[(query, passage_text), ...]`` to relevance scores.
        """
        candidates = self.hybrid(query, k=min(recall, len(self.texts)), recall=recall)
        if not candidates:
            return []
        scores = score_fn([(query, p.text) for p in candidates])
        ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)[:k]
        return [Passage(text=p.text, source=p.source, score=round(float(s), 4)) for p, s in ranked]

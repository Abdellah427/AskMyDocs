"""Build the retrieval index from documents and query it.

Three retrieval modes are exposed, all built on the same in-memory index:
dense (cosine), hybrid (dense + BM25) and rerank (hybrid recall + cross-encoder).
No LangChain, no ragatouille.
"""

import logging
from typing import List

import streamlit as st

from src.embeddings import Embedder
from src.retrieval import Passage, RagIndex

# Re-exported so existing callers keep using create_db.*.
from src.documents import (  # noqa: F401
    csv_to_list_str,
    chunk_text,
    extract_paragraphs_from_pdf,
    files_to_list_str,
    files_to_passages,
    group_paragraphs,
)

METHODS = ["Dense", "Hybride", "Rerank"]


def build_index(passages: List[Passage]) -> RagIndex:
    """Embed the passages and build the in-memory retrieval index."""
    embedder = Embedder()
    texts = [p.text for p in passages]
    embeddings = embedder.encode(texts)
    logging.info("Encoded %d passages", len(texts))
    index = RagIndex(passages=passages, embeddings=embeddings, embed_fn=embedder.encode)
    st.session_state["rag_index"] = index
    return index


def _index() -> RagIndex:
    index = st.session_state.get("rag_index")
    if index is None:
        raise ValueError("No index found. Please create the database first.")
    return index


def _as_results(passages: List[Passage]) -> List[dict]:
    return [{"source": p.source, "score": p.score, "text": p.text} for p in passages]


def query_dense(query_text: str, n_results: int = 5) -> List[dict]:
    return _as_results(_index().dense(query_text, k=n_results))


def query_hybrid(query_text: str, n_results: int = 5) -> List[dict]:
    return _as_results(_index().hybrid(query_text, k=n_results))


def query_rerank(query_text: str, n_results: int = 5) -> List[dict]:
    from src.reranker import CrossEncoderReranker

    reranker = st.session_state.get("reranker")
    if reranker is None:
        reranker = CrossEncoderReranker()
        st.session_state["reranker"] = reranker
    return _as_results(_index().rerank(query_text, score_fn=reranker.score, k=n_results))


def query(method: str, query_text: str, n_results: int = 5) -> List[dict]:
    """Dispatch a query to the selected retrieval method."""
    if method == "Dense":
        return query_dense(query_text, n_results)
    if method == "Hybride":
        return query_hybrid(query_text, n_results)
    if method == "Rerank":
        return query_rerank(query_text, n_results)
    return []

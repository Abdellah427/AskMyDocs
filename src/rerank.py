"""PCA-accelerated FAISS retrieval with a full-embedding rerank stage.

A first, fast pass searches a PCA-reduced FAISS index to recall candidate
passages, then those candidates are re-scored against the query using the full
embeddings so the final ranking is not degraded by the dimensionality reduction.
"""

from typing import Callable, List, Optional, Tuple

import faiss
import numpy as np


def _load_embedder() -> Callable[[List[str]], np.ndarray]:
    """Return the default sentence-embedding function (imported lazily)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2").encode


def load_faiss(embeddings: np.ndarray) -> Tuple[faiss.Index, faiss.VectorTransform]:
    """Build a PCA-reduced FAISS index for faster similarity search.

    Args:
        embeddings: The original embeddings to index.

    Returns:
        The trained FAISS index and the PCA matrix used to reduce dimensions.
    """
    embeddings = np.asarray(embeddings, dtype="float32")
    # PCA output dimension cannot exceed the number of features or samples.
    dimension = min(128, embeddings.shape[1], embeddings.shape[0])

    pca = faiss.PCAMatrix(embeddings.shape[1], dimension)
    pca.train(embeddings)
    reduced = pca.apply_py(embeddings)

    quantizer = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIVFFlat(quantizer, dimension, 1)
    index.train(reduced)
    index.add(reduced)
    return index, pca


def create_vector_db_all_MiniLM_L6_VS(
    data_liste: List[str], embed_fn: Optional[Callable] = None
) -> Tuple[faiss.Index, faiss.VectorTransform]:
    """Embed the documents, build a PCA-reduced FAISS index, and save it to disk.

    Args:
        data_liste: The text chunks to embed and index.
        embed_fn: Optional embedding function (defaults to all-MiniLM-L6-v2).

    Returns:
        The FAISS index and PCA matrix (also written to ``faiss_index_file`` and
        ``pca_file``).
    """
    embed = embed_fn or _load_embedder()
    embeddings = np.asarray(embed(data_liste), dtype="float32")

    index, pca = load_faiss(embeddings)
    faiss.write_index(index, "faiss_index_file")
    faiss.write_VectorTransform(pca, "pca_file")
    return index, pca


def _cosine_similarity(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """Cosine similarity between each row of ``matrix`` and ``vector``."""
    matrix_norms = np.linalg.norm(matrix, axis=1)
    vector_norm = np.linalg.norm(vector)
    denominator = matrix_norms * vector_norm + 1e-8
    return (matrix @ vector) / denominator


def search_and_rerank(
    pca: faiss.VectorTransform,
    query: str,
    index: faiss.Index,
    texts: List[str],
    embed_fn: Optional[Callable] = None,
    top_k: int = 3,
    recall_k: Optional[int] = None,
) -> List[str]:
    """Retrieve candidates from the PCA index, then rerank on full embeddings.

    Args:
        pca: The PCA matrix that reduced the indexed embeddings.
        query: The query string.
        index: The PCA-reduced FAISS index.
        texts: The passages, in the same order as the index.
        embed_fn: Optional embedding function (defaults to all-MiniLM-L6-v2).
        top_k: Number of passages to return after reranking.
        recall_k: Size of the first-pass candidate set (defaults to 4 x top_k).

    Returns:
        The top passages, each formatted with its relevance score.
    """
    if not texts:
        return []

    embed = embed_fn or _load_embedder()
    if recall_k is None:
        recall_k = min(len(texts), max(top_k * 4, top_k))

    # First pass: fast approximate recall on PCA-reduced vectors.
    query_full = np.asarray(embed([query]), dtype="float32")
    query_reduced = pca.apply_py(query_full)
    _distances, indices = index.search(query_reduced, recall_k)
    candidates = [int(i) for i in indices[0] if 0 <= i < len(texts)]
    if not candidates:
        return []

    # Second pass: rerank candidates using the full (un-reduced) embeddings.
    candidate_embeddings = np.asarray(embed([texts[i] for i in candidates]), dtype="float32")
    similarities = _cosine_similarity(candidate_embeddings, query_full[0])
    order = np.argsort(-similarities)[:top_k]

    results = []
    for rank in order:
        idx = candidates[int(rank)]
        score = round(float(similarities[int(rank)]), 3)
        results.append(f"Content: {texts[idx]}\n\n Relevance: {score}")
    return results

"""Index construction and querying for the vector and ColBERTv2 retrievers."""

import logging
from typing import List

import faiss
import numpy as np
import streamlit as st
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

# Re-exported so existing callers (interfaceG) can keep using create_db.*.
from src.documents import (  # noqa: F401
    csv_to_list_str,
    extract_paragraphs_from_pdf,
    files_to_list_str,
    group_paragraphs,
)
from src.CustomVectorRetriever import CustomVectorRetriever

# In-process cache of the ColBERT model used while building an index.
RAG_Corbert = None


def _load_ragatouille():
    """Import ragatouille lazily so the app starts even when it is missing.

    ColBERTv2 is an optional method: ragatouille pins an older LangChain, so it
    is only imported when that method is actually used.
    """
    try:
        from ragatouille import RAGPretrainedModel
    except ImportError as exc:
        raise RuntimeError(
            "The ColBERTv2 method requires the optional 'ragatouille' package "
            "(install it with a LangChain 0.3 environment). Use the Retriever or "
            "Rerank method instead."
        ) from exc
    return RAGPretrainedModel


# ----------------------------------------------------------------------------
# ColBERTv2
# ----------------------------------------------------------------------------
def create_vector_db_colbertv2(documents: List[str], max_document_length: int = 100) -> str:
    """Index a collection of documents with ColBERTv2 and return the index path.

    Args:
        documents: The text chunks to index.
        max_document_length: Maximum token length per indexed document.

    Returns:
        The path to the created index.
    """
    global RAG_Corbert
    RAG_Corbert = _load_ragatouille().from_pretrained("colbert-ir/colbertv2.0")

    index_path = RAG_Corbert.index(
        collection=documents,
        max_document_length=max_document_length,
        split_documents=True,
        use_faiss=True,
    )

    # Persist the path so the query side can reload the built index. Storing it
    # in session_state keeps it tied to the user's session rather than to a
    # module global that is shared across every Streamlit session.
    st.session_state["colbert_index_path"] = index_path
    return index_path


def query_vector_db_colbertv2(query_text: str, n_results: int = 5) -> List[dict]:
    """Query the ColBERTv2 index built by :func:`create_vector_db_colbertv2`.

    Args:
        query_text: The query string.
        n_results: Number of top results to return.

    Returns:
        The retrieved passages with their scores.
    """
    index_path = st.session_state.get("colbert_index_path")
    if not index_path:
        raise ValueError("ColBERTv2 index not found. Please create the database first.")

    # Reload the index (not a bare pretrained model) so the indexed collection is
    # attached and search actually retrieves. Cache it to avoid reloading on
    # every query.
    model = st.session_state.get("colbert_model")
    if model is None:
        model = _load_ragatouille().from_index(index_path)
        st.session_state["colbert_model"] = model

    return model.search(query_text, k=n_results)


# ----------------------------------------------------------------------------
# Vector retriever (all-MiniLM-L6-v2 + FAISS)
# ----------------------------------------------------------------------------
def create_vector_db_all_MiniLM_L6(documents: List[str]) -> None:
    """Embed the documents and build an in-memory FAISS retriever.

    The retriever is stored in ``st.session_state`` for the query step.

    Args:
        documents: The text chunks to embed and index.
    """
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = embedding_model.encode(documents, show_progress_bar=False)
    embeddings = np.asarray(embeddings, dtype="float32")
    logging.info("Encoded %d documents", len(documents))

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    docs = [Document(page_content=content, metadata={"content": content}) for content in documents]
    retriever = CustomVectorRetriever(
        embedding_function=embedding_model.encode, index=index, documents=docs
    )

    st.session_state.retriever = retriever
    st.write("Embeddings created successfully!")


def query_vector_db_CustomVectorRetriever(query_text: str, n_results: int = 5) -> List[dict]:
    """Query the in-memory FAISS retriever.

    Args:
        query_text: The query string.
        n_results: Number of results to return.

    Returns:
        The retrieved passages.
    """
    if "retriever" not in st.session_state:
        raise ValueError("Retriever not found in session state. Please create embeddings first.")

    retriever = st.session_state.retriever
    relevant_documents = retriever.retrieve(query_text, n_results)
    return [{"Content": doc.page_content} for doc in relevant_documents]

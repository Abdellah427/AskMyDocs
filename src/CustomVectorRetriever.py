"""A small FAISS-backed retriever compatible with LangChain."""

from typing import Callable, List

import numpy as np
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field


class CustomVectorRetriever(BaseRetriever):
    """Retrieve documents from a FAISS index using a text-embedding function.

    Attributes:
        embedding_function: Maps a list of strings to their vectors.
        index: A trained FAISS index over the documents.
        documents: The documents, in the same order as the index.
        k: Default number of documents to return.
    """

    # The FAISS index is an arbitrary (non-pydantic) type.
    model_config = ConfigDict(arbitrary_types_allowed=True)

    embedding_function: Callable = Field(...)
    index: object = Field(...)
    documents: List[Document] = Field(...)
    k: int = 5

    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """Return the ``k`` documents closest to ``query``.

        Args:
            query: The query string.
            k: Number of documents to return; falls back to ``self.k``.
        """
        top_k = self.k if k is None else k
        query_embedding = np.asarray(self.embedding_function([query]), dtype="float32")
        _distances, indices = self.index.search(query_embedding, top_k)
        return [self.documents[i] for i in indices[0] if 0 <= i < len(self.documents)]

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        """LangChain retriever entry point (used by ``.invoke``)."""
        return self.retrieve(query, self.k)

    async def _aget_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        """Async LangChain retriever entry point."""
        return self.retrieve(query, self.k)

"""Round-trip test for the FAISS vector retriever (CustomVectorRetriever)."""

import faiss
from langchain_core.documents import Document

from src.CustomVectorRetriever import CustomVectorRetriever
from tests.embedding import build_corpus, embed


def _build_retriever():
    docs, embeddings = build_corpus()
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    documents = [Document(page_content=d, metadata={"content": d}) for d in docs]
    return CustomVectorRetriever(embedding_function=embed, index=index, documents=documents)


def test_retriever_returns_the_matching_topic():
    retriever = _build_retriever()

    results = retriever.retrieve("tell me about the cat", k=1)

    assert len(results) == 1
    assert "cat" in results[0].page_content


def test_retriever_respects_k():
    retriever = _build_retriever()

    results = retriever.retrieve("ocean waves", k=3)

    assert len(results) == 3
    # The closest document is the strong ocean document.
    assert "ocean" in results[0].page_content


def test_retriever_langchain_invoke_entrypoint():
    # The standard LangChain entry point must work too, not just retrieve().
    retriever = _build_retriever()
    retriever.k = 2

    results = retriever.invoke("a dog in the park")

    assert len(results) == 2
    assert any("dog" in doc.page_content for doc in results)

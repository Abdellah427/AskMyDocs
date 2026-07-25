"""Tests for the grounded-prompt context builder and key guard."""

from src.llm_interface import build_context, query_mistral


def test_build_context_numbers_and_sources():
    passages = [
        {"source": "movies.csv", "text": "Titanic is a romance."},
        {"source": "notes.pdf", "text": "Rose meets Jack."},
    ]
    ctx = build_context(passages)
    assert "[1] (source: movies.csv)" in ctx
    assert "Titanic is a romance." in ctx
    assert "[2] (source: notes.pdf)" in ctx
    assert "Rose meets Jack." in ctx


def test_build_context_empty():
    assert build_context([]) == ""
    assert build_context(None) == ""


def test_query_mistral_without_key_is_graceful():
    # No key: returns a message and never imports/hits the API.
    out = query_mistral("What is this?", [], "", [{"source": "x", "text": "y"}])
    assert "MISTRAL_API_KEY" in out

"""Runtime configuration: model names and the Mistral API key.

Everything is overridable through environment variables so models can be swapped
without touching the code.
"""

import os

# Multilingual embedding model (handles French and English well, no prefix needed).
EMBEDDING_MODEL = os.environ.get(
    "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Multilingual cross-encoder used to rerank retrieved passages. This default is
# light (~120 MB); for maximum quality set RERANKER_MODEL=BAAI/bge-reranker-v2-m3.
RERANKER_MODEL = os.environ.get(
    "RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
)

# LLM used to write the final answer.
GENERATION_MODEL = os.environ.get("MISTRAL_MODEL", "mistral-large-latest")


def get_mistral_api_key() -> str:
    """Return the Mistral API key, or an empty string if none is configured.

    Resolution order:
        1. ``st.secrets["MISTRAL_API_KEY"]`` (``.streamlit/secrets.toml``)
        2. the ``MISTRAL_API_KEY`` environment variable
    """
    try:
        import streamlit as st

        # Accessing st.secrets raises if no secrets file exists, hence the guard.
        key = st.secrets.get("MISTRAL_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.environ.get("MISTRAL_API_KEY", "")

"""Runtime configuration.

The Mistral API key is read from Streamlit secrets first, then from the
``MISTRAL_API_KEY`` environment variable. It is never hard-coded in the source.
"""

import os


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

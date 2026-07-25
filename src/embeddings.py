"""Sentence-embedding model wrapper (lazy-loaded sentence-transformers)."""

from typing import List, Optional

import numpy as np

from src.config import EMBEDDING_MODEL


class Embedder:
    """Encodes text into vectors with a sentence-transformers model.

    The model is loaded on first use so importing this module stays cheap.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or EMBEDDING_MODEL
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: List[str]) -> np.ndarray:
        vectors = self._load().encode(list(texts), show_progress_bar=False)
        return np.asarray(vectors, dtype="float32")

    def __call__(self, texts: List[str]) -> np.ndarray:
        return self.encode(texts)

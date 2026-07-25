"""Cross-encoder reranker (lazy-loaded sentence-transformers CrossEncoder).

Replaces the old ColBERT/ragatouille path with a maintained, dependency-light
alternative that gives comparable precision.
"""

from typing import List, Optional, Sequence, Tuple

from src.config import RERANKER_MODEL


class CrossEncoderReranker:
    """Scores (query, passage) pairs for relevance."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or RERANKER_MODEL
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_name)
        return self._model

    def score(self, pairs: Sequence[Tuple[str, str]]) -> List[float]:
        if not pairs:
            return []
        scores = self._load().predict([list(p) for p in pairs])
        return [float(s) for s in scores]

    def __call__(self, pairs: Sequence[Tuple[str, str]]) -> List[float]:
        return self.score(pairs)

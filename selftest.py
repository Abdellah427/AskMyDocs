"""Fast self-test run by the launcher before starting the app.

Checks that the dependencies and project modules import cleanly and that the
retrieval core works on a tiny in-memory example (no model download, no network).
Exits 0 when everything is fine, 1 otherwise.
"""

import importlib
import importlib.util
import sys

ok = True


def _require(module: str) -> None:
    global ok
    if importlib.util.find_spec(module) is None:
        print(f"  MISSING dependency: {module}")
        ok = False


# 1. Dependencies present (without importing the heavy ones).
for name in ["faiss", "numpy", "pandas", "rank_bm25", "streamlit", "sentence_transformers"]:
    _require(name)

# 2. mistralai must expose the v1 client.
try:
    from mistralai import Mistral  # noqa: F401
except Exception as exc:  # noqa: BLE001
    print(f"  BROKEN: mistralai ({exc})")
    ok = False

# 3. Project modules import cleanly.
for name in [
    "src.config",
    "src.documents",
    "src.retrieval",
    "src.embeddings",
    "src.reranker",
    "src.eval",
    "src.llm_interface",
    "src.create_db",
    "src.interfaceG",
]:
    try:
        importlib.import_module(name)
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED to import {name} ({exc})")
        ok = False

# 4. Retrieval core works end to end (deterministic, no download).
try:
    import numpy as np

    from src.retrieval import Passage, RagIndex

    embeddings = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype="float32")
    index = RagIndex(
        [Passage("cat"), Passage("dog")],
        embeddings,
        lambda texts: np.array([[1.0, 0.0, 0.0]] * len(texts), dtype="float32"),
    )
    top = index.dense("query", k=1)
    if not top or top[0].text != "cat":
        print("  FAILED: retrieval returned an unexpected result")
        ok = False
except Exception as exc:  # noqa: BLE001
    print(f"  FAILED: retrieval smoke test ({exc})")
    ok = False

print("Self-test: OK" if ok else "Self-test: FAILED")
sys.exit(0 if ok else 1)

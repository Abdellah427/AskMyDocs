# AskMyDocs

A Retrieval-Augmented Generation (RAG) document assistant. Upload your CSV and
PDF files, ask questions in plain language, and get answers grounded in the
passages retrieved from your own documents, with the sources shown alongside.

Live showcase: https://abdellah-hassani.fr/askmydocs

## Overview

AskMyDocs indexes your documents locally, retrieves the passages most relevant
to a question, and uses a language model to write an answer based on them. It is
useful for exploring any corpus of unstructured text: technical documentation,
reports, research notes, or tabular data exported to CSV.

The interface is built with Streamlit. Indexing and vector search run on your
machine; only the final answer generation calls an external language model.

## Features

- **CSV and PDF input.** Import several files at once; documents are split into
  overlapping chunks so information that straddles a boundary stays retrievable.
- **Grounded answers.** The model answers only from the retrieved passages,
  cites its sources, and says when it does not know. Each passage is shown with
  its source file and relevance score.
- **Multilingual embeddings.** A multilingual sentence-transformers model, with
  cosine similarity over a FAISS index.
- **Three retrieval methods**, switchable at any time (they share one index):
  - **Dense** - normalized multilingual embeddings with FAISS cosine search. A
    fast, solid baseline.
  - **Hybrid** - dense search combined with BM25 keyword search, fused with
    Reciprocal Rank Fusion for better coverage.
  - **Rerank** - hybrid recall, then a cross-encoder re-ranks the candidates for
    top precision.

## Getting started

### Prerequisites

- Python 3.10 or newer
- A Mistral API key (for answer generation)

### Quick start

Double-click the launcher (or run it from a terminal). It checks Python, sets up
the virtual environment, installs the dependencies, runs a self-test, repairs the
environment if needed, and starts the app.

- Windows: double-click **`launch.bat`**
- Linux or macOS:

  ```bash
  ./launch.sh
  ```

### Manual setup

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows:     .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown in the terminal.

### API key

The app reads the Mistral API key from the `MISTRAL_API_KEY` environment
variable (or from a Streamlit secret). Copy `.env.example` to `.env` and set your
key; the launcher scripts load it automatically.

```bash
cp .env.example .env
# then edit .env and set MISTRAL_API_KEY
```

The key is never stored in the source code.

## Running the tests

The retrieval and document-processing logic is covered by a test suite that runs
offline (no model download required):

```bash
pip install pytest
python -m pytest
```

The tests exercise CSV parsing, overlapping chunking, the dense / hybrid /
rerank retrieval pipeline, Reciprocal Rank Fusion, recall@k evaluation, and the
grounded-prompt builder, all on a small in-memory corpus with a deterministic
stand-in embedding (no model download, no network).

## Project structure

```
app.py                 Streamlit entry point
src/
  interfaceG.py        UI flow and session handling
  documents.py         CSV/PDF loading and overlapping chunking
  embeddings.py        Sentence-transformers embedding wrapper
  retrieval.py         Dense, hybrid (BM25 + RRF) and rerank search
  reranker.py          Cross-encoder reranker
  create_db.py         Index construction and query dispatch
  llm_interface.py     Grounded answer generation with Mistral
  eval.py              recall@k evaluation
  config.py            Model names and API key resolution
tests/                 Offline test suite
site/                  Static showcase site
```

## Report

A detailed report describing the approach is available in `Rapport.pdf`.

## Authors

Developed as part of the 2024-2025 academic year at CY Tech.

- Abdellah Hassani
- Romain Guenneau
- Simon Ren
- Ritchy Agnesa

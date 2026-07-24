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

- **CSV and PDF input.** Import several files at once; spreadsheets and text
  documents alike are split into evenly sized passages.
- **Grounded answers.** Each answer comes with the retrieved passages and their
  relevance score, so you can see where the information comes from.
- **Three retrieval methods**, selectable in the interface:
  - **Retriever** - all-MiniLM-L6-v2 embeddings with a FAISS vector search.
    Light and fast, a good default for small to medium corpora.
  - **ColBERTv2** - late-interaction retrieval, where each query term is matched
    against the document for finer alignment. Best for precise questions.
  - **Rerank** - a fast first pass over a PCA-reduced FAISS index recalls
    candidates, which are then re-ranked using the full embeddings. Suited to
    larger corpora.

## Getting started

### Prerequisites

- Python 3.10 or newer
- A Mistral API key (for answer generation)

### Quick start

The launcher scripts create a virtual environment, install the dependencies, and
start the app.

- Linux or macOS:

  ```bash
  ./run.sh
  ```

- Windows:

  ```bat
  run.bat
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

The tests exercise CSV parsing, PDF-chunk grouping, the FAISS retrieval
round-trip, and the PCA + rerank pipeline on a small in-memory corpus.

## Project structure

```
app.py                 Streamlit entry point
src/
  interfaceG.py        UI flow and session handling
  documents.py         CSV/PDF loading and chunking
  create_db.py         Vector and ColBERTv2 index construction and querying
  rerank.py            PCA-accelerated FAISS search with a rerank stage
  CustomVectorRetriever.py   FAISS-backed LangChain retriever
  llm_interface.py     Mistral answer generation
  config.py            API key resolution
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

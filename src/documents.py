"""Document loading and chunking.

Pure text-processing helpers with no Streamlit or machine-learning imports, so
they stay fast to import and straightforward to unit test. Heavy, optional
dependencies (pdfplumber) are imported lazily, inside the function that needs
them.
"""

import os
from typing import Callable, List

import pandas as pd


def csv_to_list_str(csv_path: str) -> List[str]:
    """Convert a CSV file to a list of strings, one string per row.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        One string per row, formatted as "column: value" pairs.
    """
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        # Some exported CSV files use Latin-1 rather than UTF-8.
        df = pd.read_csv(csv_path, encoding="ISO-8859-1")

    rows = []
    for _, row in df.iterrows():
        row_text = [f"{column}: {row[column]}" for column in df.columns]
        rows.append(" | ".join(row_text))
    return rows


def chunk_text(text: str, max_words: int = 180, overlap_words: int = 30) -> List[str]:
    """Split text into overlapping word windows.

    Overlap keeps information that straddles a boundary retrievable from at least
    one chunk.

    Args:
        text: The text to split.
        max_words: Maximum number of words per chunk.
        overlap_words: Number of words shared between consecutive chunks.

    Returns:
        The (possibly overlapping) chunks.
    """
    words = text.split()
    if not words:
        return []
    if len(words) <= max_words:
        return [" ".join(words)]

    step = max(1, max_words - overlap_words)
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start : start + max_words]))
        if start + max_words >= len(words):
            break
    return chunks


def group_paragraphs(
    paragraphs: List[str], min_characters: int = 300, max_characters: int = 1400
) -> List[str]:
    """Group short paragraphs so each chunk sits between a minimum and a maximum
    length. Kept as a utility for callers that want paragraph-aware grouping.
    """
    grouped: List[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 1 <= max_characters:
            current += " " + paragraph
        elif len(current) < min_characters:
            current += " " + paragraph
        else:
            grouped.append(current.strip())
            current = paragraph

    if current.strip():
        grouped.append(current.strip())
    return grouped


def extract_paragraphs_from_pdf(
    pdf_path: str, max_words: int = 180, overlap_words: int = 30
) -> List[str]:
    """Extract text from a PDF and return it as overlapping chunks.

    Args:
        pdf_path: Path to the PDF file.
        max_words: Maximum number of words per chunk.
        overlap_words: Number of words shared between consecutive chunks.

    Returns:
        The extracted, overlapping chunks.
    """
    # Imported lazily: pdfplumber is only needed when a PDF is actually read.
    import pdfplumber

    pages: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Keep only characters that round-trip through UTF-8.
                pages.append(text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore"))

    return chunk_text("\n".join(pages), max_words=max_words, overlap_words=overlap_words)


def files_to_list_str(
    file_paths: List[str],
    csv_reader: Callable[[str], List[str]] = csv_to_list_str,
    pdf_reader: Callable[[str], List[str]] = extract_paragraphs_from_pdf,
) -> List[str]:
    """Read a list of CSV and/or PDF files into a single list of text chunks.

    The reader functions are injectable to keep this dispatch logic testable
    without touching the filesystem or PDF stack.
    """
    full_doc: List[str] = []
    for file_path in file_paths:
        extension = os.path.splitext(file_path)[-1].lower()
        if extension == ".csv":
            full_doc.extend(csv_reader(file_path))
        elif extension == ".pdf":
            full_doc.extend(pdf_reader(file_path))
    return full_doc


def files_to_passages(file_paths: List[str]):
    """Read files into Passage objects that carry their source filename."""
    from src.retrieval import Passage

    passages = []
    for file_path in file_paths:
        source = os.path.basename(file_path)
        for chunk in files_to_list_str([file_path]):
            passages.append(Passage(text=chunk, source=source))
    return passages

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
        row_text = [f"{column}: {row[column]}\n\n" for column in df.columns]
        rows.append(" ".join(row_text))
    return rows


def group_paragraphs(
    paragraphs: List[str], min_characters: int = 300, max_characters: int = 1400
) -> List[str]:
    """Group short paragraphs so each chunk sits between a minimum and a
    maximum length.

    A chunk keeps growing while it stays under ``max_characters``. Once adding
    the next paragraph would overflow, the chunk is emitted only if it already
    reached ``min_characters``; otherwise the paragraph is merged in anyway so a
    chunk is never left too small to be useful.

    Args:
        paragraphs: Cleaned, non-empty paragraphs in reading order.
        min_characters: Minimum size before a chunk may be emitted.
        max_characters: Preferred maximum size for a chunk.

    Returns:
        The grouped chunks.
    """
    grouped: List[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 1 <= max_characters:
            current += " " + paragraph
        elif len(current) < min_characters:
            # Too small to stand alone: merge even if it overflows the maximum.
            current += " " + paragraph
        else:
            grouped.append(current.strip())
            current = paragraph

    if current.strip():
        grouped.append(current.strip())
    return grouped


def extract_paragraphs_from_pdf(
    pdf_path: str, min_characters: int = 300, max_characters: int = 1400
) -> List[str]:
    """Extract text from a PDF and return it as length-bounded chunks.

    Args:
        pdf_path: Path to the PDF file.
        min_characters: Minimum size before a chunk may be emitted.
        max_characters: Preferred maximum size for a chunk.

    Returns:
        The extracted, grouped chunks.
    """
    # Imported lazily: pdfplumber is only needed when a PDF is actually read.
    import pdfplumber

    paragraphs: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Keep only characters that round-trip through UTF-8.
                utf8_text = text.encode("utf-8", errors="ignore").decode(
                    "utf-8", errors="ignore"
                )
                paragraphs.extend(utf8_text.split("\n\n"))

    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return group_paragraphs(paragraphs, min_characters, max_characters)


def files_to_list_str(
    file_paths: List[str],
    csv_reader: Callable[[str], List[str]] = csv_to_list_str,
    pdf_reader: Callable[[str], List[str]] = extract_paragraphs_from_pdf,
) -> List[str]:
    """Read a list of CSV and/or PDF files into a single list of text chunks.

    The reader functions are injectable to keep this dispatch logic testable
    without touching the filesystem or PDF stack.

    Args:
        file_paths: Paths to CSV or PDF files.
        csv_reader: Function used to read a CSV file.
        pdf_reader: Function used to read a PDF file.

    Returns:
        The concatenated chunks from every supported file.
    """
    full_doc: List[str] = []
    for file_path in file_paths:
        extension = os.path.splitext(file_path)[-1].lower()
        if extension == ".csv":
            full_doc.extend(csv_reader(file_path))
        elif extension == ".pdf":
            full_doc.extend(pdf_reader(file_path))
    return full_doc

"""Tests for document loading and chunking (src/documents.py)."""

import csv

from src.documents import chunk_text, csv_to_list_str, files_to_list_str, group_paragraphs


def test_csv_round_trip(tmp_path):
    path = tmp_path / "movies.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "plot"])
        writer.writerow(["Titanic", "A love story aboard a liner"])
        writer.writerow(["The Lion King", "A young lion becomes king"])

    rows = csv_to_list_str(str(path))

    assert len(rows) == 2
    assert "title: Titanic" in rows[0]
    assert "plot: A love story aboard a liner" in rows[0]
    assert "The Lion King" in rows[1]


def test_csv_latin1_fallback(tmp_path):
    # A file that is not valid UTF-8 must still be read via the Latin-1 fallback.
    path = tmp_path / "accents.csv"
    with open(path, "w", newline="", encoding="ISO-8859-1") as f:
        f.write("titre;resume\n")
        f.write("Amelie;Une resume en francais avec des accents: eaeu\n")
    # Written with ';' so pandas keeps a single column; the point is decoding.
    path.write_bytes("titre\nrésumé cliché déjà\n".encode("ISO-8859-1"))

    rows = csv_to_list_str(str(path))

    assert len(rows) == 1
    assert "résumé cliché déjà" in rows[0]


def test_files_to_list_str_dispatch():
    calls = {"csv": [], "pdf": []}

    def fake_csv(path):
        calls["csv"].append(path)
        return [f"CSV::{path}"]

    def fake_pdf(path):
        calls["pdf"].append(path)
        return [f"PDF::{path}"]

    result = files_to_list_str(
        ["a.csv", "b.pdf", "c.txt", "d.CSV"],
        csv_reader=fake_csv,
        pdf_reader=fake_pdf,
    )

    # .txt is ignored; extension matching is case-insensitive.
    assert result == ["CSV::a.csv", "PDF::b.pdf", "CSV::d.CSV"]
    assert calls["csv"] == ["a.csv", "d.CSV"]
    assert calls["pdf"] == ["b.pdf"]


def test_chunk_text_empty_and_short():
    assert chunk_text("") == []
    assert chunk_text("just a few words", max_words=10) == ["just a few words"]


def test_chunk_text_overlap():
    text = " ".join(f"w{i}" for i in range(100))
    chunks = chunk_text(text, max_words=40, overlap_words=10)

    assert len(chunks) > 1
    # Every chunk (but the last) has the max size.
    assert all(len(c.split()) == 40 for c in chunks[:-1])
    # Consecutive chunks overlap by exactly overlap_words.
    first_words = chunks[0].split()
    second_words = chunks[1].split()
    assert first_words[-10:] == second_words[:10]
    # No word is lost.
    assert first_words[0] == "w0" and chunks[-1].split()[-1] == "w99"


def test_group_paragraphs_empty():
    assert group_paragraphs([]) == []


def test_group_paragraphs_single_short():
    assert group_paragraphs(["hello"], min_characters=300, max_characters=1400) == ["hello"]


def test_group_paragraphs_merges_until_max():
    paragraphs = ["a" * 100, "b" * 100, "c" * 100, "d" * 100]
    chunks = group_paragraphs(paragraphs, min_characters=150, max_characters=250)

    assert len(chunks) == 2
    # First chunk pairs a+b, second pairs c+d.
    assert chunks[0].count("a") == 100 and chunks[0].count("b") == 100
    assert chunks[1].count("c") == 100 and chunks[1].count("d") == 100
    # Grouping keeps chunks at or above the minimum (except a trailing remainder).
    assert all(len(c) >= 150 for c in chunks)


def test_group_paragraphs_merges_small_even_past_max():
    # A chunk below the minimum keeps absorbing paragraphs even if it overflows
    # the maximum, so no chunk is left too small to be useful.
    paragraphs = ["x" * 50, "y" * 50, "z" * 300]
    chunks = group_paragraphs(paragraphs, min_characters=200, max_characters=100)

    assert len(chunks) == 1
    assert len(chunks[0]) > 100

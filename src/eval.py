"""Lightweight retrieval evaluation: recall@k over a labelled question set."""

from typing import Callable, List, Sequence

from src.retrieval import Passage


def recall_at_k(
    retrieve: Callable[[str, int], Sequence[Passage]],
    questions: Sequence[str],
    expected_substrings: Sequence[str],
    k: int = 5,
) -> float:
    """Fraction of questions whose expected passage appears in the top ``k``.

    Args:
        retrieve: Function ``(query, k) -> passages``.
        questions: The evaluation questions.
        expected_substrings: For each question, a substring that must appear in
            at least one retrieved passage for it to count as a hit.
        k: Cut-off rank.

    Returns:
        Recall@k in ``[0, 1]``.
    """
    if not questions:
        return 0.0

    hits = 0
    for question, needle in zip(questions, expected_substrings):
        passages = retrieve(question, k)
        if any(needle.lower() in p.text.lower() for p in passages):
            hits += 1
    return hits / len(questions)

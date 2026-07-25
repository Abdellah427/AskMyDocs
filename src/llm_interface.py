"""Answer generation with Mistral, grounded in the retrieved passages."""

from typing import List, Optional

from src.config import GENERATION_MODEL

SYSTEM_PROMPT = (
    "You are a careful documentation assistant. Answer the user's question using "
    "ONLY the provided sources. Cite the sources you rely on as [1], [2], etc. "
    "If the answer is not in the sources, say clearly that you don't know rather "
    "than guessing. Reply in the same language as the question, and stay concise."
)


def build_context(passages: Optional[List[dict]]) -> str:
    """Format retrieved passages as a numbered, source-labelled context block."""
    if not passages:
        return ""
    blocks = []
    for i, passage in enumerate(passages, start=1):
        source = passage.get("source") or "document"
        text = passage.get("text", "")
        blocks.append(f"[{i}] (source: {source})\n{text}")
    return "\n\n".join(blocks)


def query_mistral(
    user_input: str,
    history: List[str],
    api_key: str,
    passages: Optional[List[dict]] = None,
) -> str:
    """Generate an answer grounded in the retrieved passages.

    Args:
        user_input: The user's question.
        history: Previous conversation lines.
        api_key: The Mistral API key.
        passages: Retrieved passages (dicts with ``source``/``text``).

    Returns:
        The model's answer, or a short message on failure / missing key.
    """
    if not api_key:
        return "No Mistral API key is configured. Set MISTRAL_API_KEY to enable answers."

    context = build_context(passages)
    if not context:
        context = "(no sources retrieved)"

    recent = "\n".join(history[-4:])
    user_content = (
        (f"Conversation so far:\n{recent}\n\n" if recent else "")
        + f"Sources:\n{context}\n\nQuestion: {user_input}"
    )

    try:
        from mistralai import Mistral
    except ImportError:
        return (
            "The 'mistralai' package (>= 1.0) is not installed correctly. "
            'Reinstall it with: pip install --force-reinstall "mistralai>=1.0"'
        )

    try:
        client = Mistral(api_key=api_key)
        response = client.chat.complete(
            model=GENERATION_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            max_tokens=600,
            temperature=0.2,
            top_p=0.9,
        )
        return response.choices[0].message.content
    except Exception as exc:
        print(f"Detailed error: {exc}")
        return f"The request to the model failed: {type(exc).__name__}: {exc}"

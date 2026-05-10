"""Text chunking helpers for future LLM requests."""

from __future__ import annotations


def chunk_text(text: str, max_characters: int = 4000) -> list[str]:
    """Split text into simple character chunks for MVP processing."""

    if max_characters <= 0:
        raise ValueError("max_characters must be greater than zero.")

    cleaned = text.strip()
    if not cleaned:
        return []

    return [
        cleaned[start : start + max_characters]
        for start in range(0, len(cleaned), max_characters)
    ]

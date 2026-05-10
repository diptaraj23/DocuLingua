"""Text chunking helpers for future LLM requests."""

from __future__ import annotations


def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list[str]:
    """Split text into deterministic chunks, preferring paragraph boundaries."""

    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero.")
    if overlap < 0:
        raise ValueError("overlap must be zero or greater.")
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars.")

    cleaned = text.strip()
    if not cleaned:
        return []

    paragraphs = [paragraph.strip() for paragraph in cleaned.split("\n\n") if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_text(paragraph, max_chars, overlap))
            continue

        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current.strip())
            current = _add_overlap(current, paragraph, overlap, max_chars)

    if current:
        chunks.append(current.strip())

    return [chunk for chunk in chunks if chunk.strip()]


def _split_long_text(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split a single long paragraph into fixed-size chunks."""

    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunk = text[start : start + max_chars].strip()
        if chunk:
            chunks.append(chunk)
        if start + max_chars >= len(text):
            break
        start += max_chars - overlap
    return chunks


def _add_overlap(
    previous_chunk: str,
    next_paragraph: str,
    overlap: int,
    max_chars: int,
) -> str:
    """Prefix a new chunk with a small suffix from the previous chunk."""

    if overlap == 0:
        return next_paragraph
    prefix = previous_chunk[-overlap:].strip()
    candidate = f"{prefix}\n\n{next_paragraph}" if prefix else next_paragraph
    return candidate if len(candidate) <= max_chars else next_paragraph

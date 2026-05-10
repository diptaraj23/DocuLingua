"""Text cleaning utilities for extracted document text."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Normalize text while preserving reasonable paragraph breaks."""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t\f\v]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def is_text_too_short(text: str, min_chars: int = 200) -> bool:
    """Return True when cleaned text is shorter than the MVP threshold."""

    return len(clean_text(text)) < min_chars

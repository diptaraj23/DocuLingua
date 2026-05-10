"""Basic text statistics for document previews."""

from __future__ import annotations

import math
import re
from typing import Any


WORD_PATTERN = re.compile(r"\b[\w'-]+\b", flags=re.UNICODE)


def get_text_statistics(text: str) -> dict[str, Any]:
    """Calculate language-agnostic statistics for cleaned document text."""

    stripped = text.strip()
    words = WORD_PATTERN.findall(stripped.lower())
    paragraphs = [paragraph for paragraph in re.split(r"\n\s*\n", stripped) if paragraph.strip()]
    word_count = len(words)

    return {
        "character_count": len(stripped),
        "word_count": word_count,
        "paragraph_count": len(paragraphs),
        "estimated_reading_minutes": max(1, math.ceil(word_count / 200)) if word_count else 0,
        "unique_word_count": len(set(words)),
    }

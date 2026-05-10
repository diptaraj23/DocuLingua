"""Text cleaning utilities for extracted document text."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph boundaries."""

    stripped = text.strip()
    stripped = re.sub(r"[ \t]+", " ", stripped)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    return stripped

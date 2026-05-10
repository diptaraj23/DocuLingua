"""Utilities for parsing future structured LLM responses."""

from __future__ import annotations

import json
from typing import Any


def parse_json_response(response_text: str) -> dict[str, Any]:
    """Parse a JSON response string into a dictionary."""

    parsed = json.loads(response_text)
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object from the LLM response.")
    return parsed


def safe_text(response_text: str) -> str:
    """Trim a text response for downstream use."""

    return response_text.strip()

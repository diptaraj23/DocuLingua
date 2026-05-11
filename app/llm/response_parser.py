"""Robust helpers for parsing structured LLM responses."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json_text(raw_text: str) -> str:
    """Extract the first parseable JSON object or array from raw LLM text."""

    text = raw_text.strip()
    if not text:
        raise ValueError("The model response was empty and did not contain JSON.")

    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()

    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character not in "[{":
            continue
        try:
            _, end_index = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        return text[index : index + end_index]

    raise ValueError("No JSON object or array was found in the model response.")


def parse_json_response(raw_text: str) -> dict[str, Any] | list[Any]:
    """Parse an LLM response into a dictionary or list."""

    json_text = extract_json_text(raw_text)
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as error:
        raise ValueError("The model returned JSON-like text, but it could not be parsed.") from error

    if not isinstance(parsed, (dict, list)):
        raise ValueError("The model response JSON must be an object or array.")
    return parsed


def normalize_to_list(value: Any) -> list[Any]:
    """Normalize a value into a list."""

    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def safe_get_list(payload: dict[str, Any], key: str) -> list[Any]:
    """Safely return a dictionary value as a list."""

    if not isinstance(payload, dict):
        return []
    value = payload.get(key)
    return value if isinstance(value, list) else []


def safe_text(response_text: str) -> str:
    """Trim a text response for downstream use."""

    return response_text.strip()

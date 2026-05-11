"""Google Gemini LLM provider implementation."""

from __future__ import annotations

from typing import Any

from app.config import settings
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.exceptions import (
    LLMInvalidJSONError,
    LLMProviderError,
    LLMProviderNotConfiguredError,
    LLMRateLimitError,
)
from app.llm.response_parser import parse_json_response


class GeminiProvider(BaseLLMProvider):
    """JSON-focused provider wrapper for Google Gemini."""

    name = "gemini"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = settings.gemini_api_key if api_key is None else api_key
        self.main_model = settings.gemini_main_model
        self.fast_model = settings.gemini_fast_model
        self._client = None

    def is_configured(self) -> bool:
        """Return whether a Gemini API key is available."""

        return bool(self.api_key)

    def generate_json(
        self,
        prompt: str,
        section_name: str,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        retries: int = 1,
        json_schema: dict[str, Any] | None = None,
        schema_name: str | None = None,
    ) -> dict[str, Any]:
        """Generate parsed JSON from Gemini."""

        if not self.is_configured():
            raise LLMProviderNotConfiguredError("Gemini API key is missing.")

        selected_model = model or self.main_model
        attempts = max(0, retries) + 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = self._client_instance().models.generate_content(
                    model=selected_model,
                    contents=_retry_prompt(prompt) if attempt else prompt,
                    config={
                        "temperature": temperature if attempt == 0 else 0.0,
                        "max_output_tokens": max_tokens,
                        "response_mime_type": "application/json",
                    },
                )
                return _parse_gemini_json(_response_text(response))
            except LLMInvalidJSONError as error:
                last_error = error
            except Exception as error:
                if _looks_like_rate_limit(error):
                    raise LLMRateLimitError("Gemini rate limit reached.") from error
                raise LLMProviderError(f"Gemini request failed: {error}") from error

        raise LLMInvalidJSONError("Gemini did not return valid JSON after retrying.") from last_error

    def _client_instance(self):
        if self._client is None:
            try:
                from google import genai
            except ImportError as error:
                raise LLMProviderNotConfiguredError(
                    "google-genai is not installed. Run pip install -r requirements.txt."
                ) from error
            self._client = genai.Client(api_key=self.api_key)
        return self._client


def _response_text(response) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text
    candidates = getattr(response, "candidates", None) or []
    parts: list[str] = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) or []:
            value = getattr(part, "text", None)
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(parts)


def _parse_gemini_json(content: str) -> dict[str, Any]:
    if not content or not content.strip():
        raise LLMInvalidJSONError("Gemini returned an empty response.")
    try:
        parsed = parse_json_response(content)
    except ValueError as error:
        raise LLMInvalidJSONError("Gemini returned invalid JSON.") from error
    if not isinstance(parsed, dict):
        raise LLMInvalidJSONError("Gemini returned a JSON array, but an object was expected.")
    return parsed


def _looks_like_rate_limit(error: Exception) -> bool:
    text = str(error).lower()
    return "429" in text or "rate limit" in text or "too many requests" in text or "quota" in text


def _retry_prompt(prompt: str) -> str:
    return (
        f"{prompt}\n\n"
        "FINAL RETRY INSTRUCTION: Return exactly one valid JSON object only. "
        "No markdown fences, no headings, no copied source text, no explanation."
    )

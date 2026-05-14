"""Groq LLM provider implementation."""

from __future__ import annotations

from typing import Any

from groq import BadRequestError, Groq, RateLimitError

from app.config import settings
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.exceptions import (
    LLMInvalidJSONError,
    LLMProviderError,
    LLMProviderNotConfiguredError,
    LLMRateLimitError,
)
from app.llm.response_parser import parse_json_response


class GroqProvider(BaseLLMProvider):
    """JSON-focused provider wrapper for Groq."""

    name = "groq"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = settings.groq_api_key if api_key is None else api_key
        self.main_model = settings.groq_main_model
        self.fast_model = settings.groq_fast_model
        self._client: Groq | None = None

    def is_configured(self) -> bool:
        """Return whether a Groq API key is available."""

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
        """Generate parsed JSON from Groq."""

        if not self.is_configured():
            raise LLMProviderNotConfiguredError("Groq API key is missing.")

        selected_model = model or self.main_model
        attempts = max(0, retries) + 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = self._client_instance().chat.completions.create(
                    **self._completion_kwargs(
                        prompt=_retry_prompt(prompt) if attempt else prompt,
                        model=selected_model,
                        temperature=temperature if attempt == 0 else 0.0,
                        max_tokens=max_tokens,
                        json_schema=json_schema if attempt == 0 else None,
                        schema_name=schema_name or section_name.replace(" ", "_").lower(),
                        use_json_object_mode=attempt == 0 and json_schema is None,
                    )
                )
                content = response.choices[0].message.content if response.choices else ""
                return _parse_provider_json(content, provider_name=self.name)
            except RateLimitError as error:
                raise LLMRateLimitError("Groq rate limit reached.") from error
            except BadRequestError as error:
                recovered = _recover_failed_generation(error)
                if recovered is not None:
                    return recovered
                last_error = error
                if _looks_like_rate_limit(error):
                    raise LLMRateLimitError("Groq rate limit reached.") from error
            except LLMInvalidJSONError as error:
                last_error = error
            except Exception as error:
                if _looks_like_rate_limit(error):
                    raise LLMRateLimitError("Groq rate limit reached.") from error
                raise LLMProviderError(f"Groq request failed: {error}") from error

        raise LLMInvalidJSONError("Groq did not return valid JSON after retrying.") from last_error

    def _client_instance(self) -> Groq:
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def _completion_kwargs(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        json_schema: dict[str, Any] | None,
        schema_name: str,
        use_json_object_mode: bool,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a strict JSON API. Return exactly one valid JSON object. "
                        "Do not include prose, markdown, source text, or extra braces."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_schema:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": json_schema,
                },
            }
        elif use_json_object_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return kwargs


def _parse_provider_json(content: str, provider_name: str) -> dict[str, Any]:
    """Parse provider text into one JSON object."""

    if not content or not content.strip():
        raise LLMInvalidJSONError(f"{provider_name} returned an empty response.")
    try:
        parsed = parse_json_response(content)
    except ValueError as error:
        raise LLMInvalidJSONError(f"{provider_name} returned invalid JSON.") from error
    if not isinstance(parsed, dict):
        raise LLMInvalidJSONError(f"{provider_name} returned a JSON array, but an object was expected.")
    return parsed


def _recover_failed_generation(error: BadRequestError) -> dict[str, Any] | None:
    body = getattr(error, "body", None)
    if not isinstance(body, dict):
        return None
    error_payload = body.get("error")
    if not isinstance(error_payload, dict):
        return None
    failed_generation = error_payload.get("failed_generation")
    if not isinstance(failed_generation, str):
        return None
    try:
        parsed = parse_json_response(failed_generation)
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _looks_like_rate_limit(error: Exception) -> bool:
    text = str(error).lower()
    return (
        "429" in text
        or "rate limit" in text
        or "rate_limit" in text
        or "too many requests" in text
        or "tokens per minute" in text
        or "tpm" in text
        or "request too large" in text
    )


def _retry_prompt(prompt: str) -> str:
    return (
        f"{prompt}\n\n"
        "FINAL RETRY INSTRUCTION: Return exactly one valid JSON object only. "
        "No markdown fences, no headings, no copied source text, no explanation."
    )

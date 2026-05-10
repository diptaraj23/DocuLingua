"""Groq API wrapper for JSON-focused MVP content generation."""

from __future__ import annotations

import json
from typing import Any

from groq import BadRequestError, Groq

from app.config import settings


class GroqClient:
    """Small client wrapper that centralizes Groq API access."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        self.model = model or settings.groq_main_model
        self.fast_model = settings.groq_fast_model
        self._client: Groq | None = None

    def generate_json(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Send a prompt to Groq and parse the JSON response."""

        if not self.api_key:
            raise ValueError(
                "Groq API key is missing. Add GROQ_API_KEY to your .env file and try again."
            )

        client = self._get_client()
        selected_model = model or self.model

        try:
            response = self._create_completion(
                client=client,
                model=selected_model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                force_json_mode=True,
            )
        except BadRequestError as error:
            recovered = _recover_failed_generation(error)
            if recovered is not None:
                return recovered
            response = self._create_completion(
                client=client,
                model=selected_model,
                prompt=(
                    f"{prompt}\n\n"
                    "FINAL RETRY INSTRUCTION: output exactly one valid JSON object only. "
                    "No markdown, no headings, no copied source text, no explanation."
                ),
                temperature=0.0,
                max_tokens=max_tokens,
                force_json_mode=False,
            )

        content = response.choices[0].message.content if response.choices else ""
        if not content or not content.strip():
            raise ValueError("Groq returned an empty response. Please try again with a shorter document.")

        return _parse_json_object(content)

    def _get_client(self) -> Groq:
        """Create the Groq client lazily so tests can use fake clients."""

        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def _create_completion(
        self,
        client: Groq,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        force_json_mode: bool,
    ):
        """Create a Groq chat completion, optionally using provider JSON mode."""

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
        if force_json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return client.chat.completions.create(**kwargs)


def _parse_json_object(content: str) -> dict[str, Any]:
    """Parse one JSON object, recovering from surrounding stray text if needed."""

    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for index, character in enumerate(content):
        if character != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(content[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            candidates.append(parsed)

    if candidates:
        return candidates[-1]

    raise ValueError("Groq returned text that was not valid JSON. Please try again.")


def _recover_failed_generation(error: BadRequestError) -> dict[str, Any] | None:
    """Recover JSON from Groq json_validate_failed payloads when possible."""

    body = getattr(error, "body", None)
    if not isinstance(body, dict):
        return None
    error_payload = body.get("error")
    if not isinstance(error_payload, dict):
        return None
    failed_generation = error_payload.get("failed_generation")
    if not isinstance(failed_generation, str) or not failed_generation.strip():
        return None

    try:
        return _parse_json_object(failed_generation)
    except ValueError:
        return None

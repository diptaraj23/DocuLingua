"""Legacy Groq client wrapper kept for backwards compatibility."""

from __future__ import annotations

from typing import Any

from app.llm.providers.groq_provider import GroqProvider


class GroqClient:
    """Compatibility wrapper around the modular GroqProvider."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.provider = GroqProvider(api_key=api_key)
        if model:
            self.provider.main_model = model

    def generate_json(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        retries: int = 1,
        json_schema: dict[str, Any] | None = None,
        schema_name: str = "doculingua_section",
        strict_schema: bool = True,
    ) -> dict[str, Any]:
        """Generate parsed JSON with Groq using the provider implementation."""

        self.provider._client = self._get_client()
        return self.provider.generate_json(
            prompt=prompt,
            section_name=schema_name,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            retries=retries,
            json_schema=json_schema,
            schema_name=schema_name,
        )

    def _get_client(self):
        """Return the underlying Groq client; useful for legacy tests."""

        return self.provider._client_instance()

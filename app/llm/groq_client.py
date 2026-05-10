"""Placeholder wrapper for future Groq API calls."""

from __future__ import annotations

from app.config import settings


class GroqClient:
    """Small client wrapper that will centralize Groq API access later."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        self.model = model or settings.groq_main_model

    def generate(self, prompt: str) -> str:
        """Return generated text in a future implementation.

        This method intentionally does not call the Groq API yet.
        """

        raise NotImplementedError("Groq generation will be implemented in a later phase.")

"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Common interface for JSON-returning LLM providers."""

    name: str
    main_model: str
    fast_model: str

    @abstractmethod
    def is_configured(self) -> bool:
        """Return whether the provider has the required credentials."""

    @abstractmethod
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
        """Return parsed JSON for one section."""

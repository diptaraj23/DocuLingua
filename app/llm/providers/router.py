"""Provider router with fallback and validation support."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.config import settings
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.exceptions import LLMProviderError, LLMValidationError
from app.llm.providers.gemini_provider import GeminiProvider
from app.llm.providers.groq_provider import GroqProvider
from app.llm.providers.metadata import GenerationAttempt, SectionGenerationMetadata


SUPPORTED_PROVIDER_NAMES = {"groq", "gemini"}


class ProviderRouter:
    """Try configured LLM providers in order until one returns validated content."""

    def __init__(self, providers: list[BaseLLMProvider] | None = None) -> None:
        self.providers = providers if providers is not None else _providers_from_settings()

    def generate_json_with_fallback(
        self,
        prompt: str,
        section_name: str,
        model_type: str = "main",
        temperature: float = 0.2,
        max_tokens: int = 2000,
        retries_per_provider: int = 1,
        json_schema: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], SectionGenerationMetadata]:
        """Return parsed JSON from the first successful provider."""

        return self.generate_validated_json_with_fallback(
            prompt=prompt,
            section_name=section_name,
            validator=lambda payload: payload,
            model_type=model_type,
            temperature=temperature,
            max_tokens=max_tokens,
            retries_per_provider=retries_per_provider,
            json_schema=json_schema,
        )

    def generate_validated_json_with_fallback(
        self,
        prompt: str,
        section_name: str,
        validator: Callable[[dict[str, Any]], Any],
        model_type: str = "main",
        temperature: float = 0.2,
        max_tokens: int = 2000,
        retries_per_provider: int = 1,
        json_schema: dict[str, Any] | None = None,
    ) -> tuple[Any, SectionGenerationMetadata]:
        """Generate JSON and validate it before accepting a provider response."""

        metadata = SectionGenerationMetadata(section_name=section_name)
        for provider in self.providers:
            model = provider.fast_model if model_type == "fast" else provider.main_model
            try:
                payload = provider.generate_json(
                    prompt=prompt,
                    section_name=section_name,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retries=retries_per_provider,
                    json_schema=json_schema,
                    schema_name=section_name.replace(" ", "_").replace("&", "and").lower(),
                )
                try:
                    validated = validator(payload)
                except Exception as error:
                    raise LLMValidationError(f"{section_name} schema validation failed: {error}") from error
                metadata.provider = provider.name
                metadata.model = model
                metadata.success = True
                metadata.attempts.append(
                    GenerationAttempt(
                        provider=provider.name,
                        model=model,
                        section_name=section_name,
                        success=True,
                    )
                )
                return validated, metadata
            except Exception as error:
                metadata.attempts.append(
                    GenerationAttempt(
                        provider=provider.name,
                        model=model,
                        section_name=section_name,
                        success=False,
                        error_type=type(error).__name__,
                        error_message=str(error),
                    )
                )

        attempts = "; ".join(
            f"{attempt.provider}/{attempt.model}: {attempt.error_type}: {attempt.error_message}"
            for attempt in metadata.attempts
        )
        raise LLMProviderError(f"All LLM providers failed for {section_name}. Attempts: {attempts}")


def _providers_from_settings() -> list[BaseLLMProvider]:
    providers: list[BaseLLMProvider] = []
    for provider_name in settings.provider_order:
        if provider_name == "groq":
            providers.append(GroqProvider())
        elif provider_name == "gemini":
            providers.append(GeminiProvider())
        else:
            supported = ", ".join(sorted(SUPPORTED_PROVIDER_NAMES))
            raise LLMProviderError(
                f"Unsupported LLM provider '{provider_name}'. Supported providers: {supported}."
            )
    return providers

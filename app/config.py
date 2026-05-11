"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the DocuLingua MVP."""

    groq_api_key: str = ""
    groq_main_model: str = "openai/gpt-oss-120b"
    groq_fast_model: str = "openai/gpt-oss-20b"
    gemini_api_key: str = ""
    gemini_main_model: str = "gemini-2.5-flash"
    gemini_fast_model: str = "gemini-2.5-flash-lite"
    primary_llm_provider: str = "groq"
    fallback_llm_providers: str = "gemini"
    project_root: Path = Path(__file__).resolve().parents[1]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def provider_order(self) -> list[str]:
        """Return configured provider names in the order they should be tried."""

        providers = [self.primary_llm_provider]
        providers.extend(
            provider.strip()
            for provider in self.fallback_llm_providers.split(",")
            if provider.strip()
        )
        seen: set[str] = set()
        ordered: list[str] = []
        for provider in providers:
            normalized = provider.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered or ["groq", "gemini"]


settings = Settings()

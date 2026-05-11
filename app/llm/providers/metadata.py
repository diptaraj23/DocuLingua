"""Generation metadata models for LLM provider attempts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GenerationAttempt(BaseModel):
    """One provider attempt for one guide section."""

    provider: str
    model: str
    section_name: str
    success: bool
    error_type: str | None = None
    error_message: str | None = None


class SectionGenerationMetadata(BaseModel):
    """Provider metadata for one generated guide section."""

    section_name: str
    provider: str | None = None
    model: str | None = None
    success: bool = False
    attempts: list[GenerationAttempt] = Field(default_factory=list)


class GuideGenerationMetadata(BaseModel):
    """Provider metadata for a complete guide."""

    sections: list[SectionGenerationMetadata] = Field(default_factory=list)

    def get_successful_sections(self) -> list[str]:
        """Return names of sections generated successfully by an LLM provider."""

        return [section.section_name for section in self.sections if section.success]

    def get_failed_sections(self) -> list[str]:
        """Return names of sections that did not have successful provider output."""

        return [section.section_name for section in self.sections if not section.success]

    def to_display_rows(self) -> list[dict[str, str]]:
        """Return simple rows suitable for Streamlit tables or PDF templates."""

        rows: list[dict[str, str]] = []
        for section in self.sections:
            failed_attempts = [
                f"{attempt.provider}: {attempt.error_type or 'error'}"
                for attempt in section.attempts
                if not attempt.success
            ]
            rows.append(
                {
                    "section_name": section.section_name,
                    "provider": section.provider or "Mock fallback",
                    "model": section.model or "",
                    "status": "Generated" if section.success else "Fallback",
                    "failed_attempts": "; ".join(failed_attempts),
                }
            )
        return rows

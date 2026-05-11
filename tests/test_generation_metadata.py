from app.llm.providers.metadata import GenerationAttempt, GuideGenerationMetadata, SectionGenerationMetadata


def test_generation_metadata_display_rows() -> None:
    section = SectionGenerationMetadata(
        section_name="Key Vocabulary",
        provider="groq",
        model="model-a",
        success=True,
        attempts=[
            GenerationAttempt(
                provider="groq",
                model="model-a",
                section_name="Key Vocabulary",
                success=True,
            )
        ],
    )
    metadata = GuideGenerationMetadata(sections=[section])

    rows = metadata.to_display_rows()

    assert metadata.get_successful_sections() == ["Key Vocabulary"]
    assert metadata.get_failed_sections() == []
    assert rows[0]["provider"] == "groq"
    assert rows[0]["model"] == "model-a"

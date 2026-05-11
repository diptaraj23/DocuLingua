from app.learning.content_schema import DocumentOverview, VocabularyItem
from app.learning.llm_guide_generator import generate_key_vocabulary_with_llm, generate_overview_with_llm


class FakeRouter:
    def __init__(self, payload) -> None:
        self.payload = payload

    def generate_validated_json_with_fallback(self, prompt, section_name, validator, **kwargs):
        from app.llm.providers.metadata import SectionGenerationMetadata

        return validator(self.payload), SectionGenerationMetadata(
            section_name=section_name,
            provider="gemini",
            model="fake-model",
            success=True,
        )


def test_generate_overview_with_llm_returns_model_and_metadata() -> None:
    overview, metadata = generate_overview_with_llm(
        clean_text="La musique organise le rythme.",
        stats={"word_count": 5},
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        provider_router=FakeRouter(
            {
                "summary": "A music text.",
                "estimated_level": "A2",
                "difficulty_notes": "Simple.",
                "main_learning_focus": ["music vocabulary"],
                "suggested_study_approach": ["review words"],
            }
        ),
    )

    assert isinstance(overview, DocumentOverview)
    assert metadata.provider == "gemini"


def test_generate_key_vocabulary_with_llm_returns_items_and_metadata() -> None:
    vocabulary, metadata = generate_key_vocabulary_with_llm(
        clean_text="La musique organise le rythme.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        provider_router=FakeRouter(
            {
                "key_vocabulary": [
                    {
                        "word": "la musique",
                        "meaning": "music",
                        "part_of_speech": "noun",
                        "why_useful": "Topic word.",
                    }
                ]
            }
        ),
    )

    assert isinstance(vocabulary[0], VocabularyItem)
    assert metadata.success is True

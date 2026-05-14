import pytest

from app.learning.content_schema import LearningGuide
from app.learning.guide_polisher import polish_key_vocabulary_with_llm, polish_learning_guide_with_llm
from app.learning.mock_guide_generator import create_mock_learning_guide
from app.llm.providers.metadata import GuideGenerationMetadata, SectionGenerationMetadata


class FakeRouter:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def generate_validated_json_with_fallback(self, prompt, section_name, validator, **kwargs):
        return validator(self.payload), SectionGenerationMetadata(
            section_name=section_name,
            provider="groq",
            model="polisher-model",
            success=True,
        )


def _guide() -> LearningGuide:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )
    guide.generation_metadata = GuideGenerationMetadata(
        sections=[SectionGenerationMetadata(section_name="Key Vocabulary", provider="groq", model="m", success=True)]
    )
    return guide


def test_polish_learning_guide_with_llm_returns_learning_guide() -> None:
    guide = _guide()
    payload = guide.model_dump(mode="json")
    payload["title"] = "Polished DocuLingua Workbook"

    polished, metadata = polish_learning_guide_with_llm(
        guide,
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        provider_router=FakeRouter(payload),
    )

    assert isinstance(polished, LearningGuide)
    assert polished.title == "Polished DocuLingua Workbook"
    assert polished.key_vocabulary
    assert metadata.provider == "groq"


def test_polisher_preserves_generation_metadata_when_response_drops_it() -> None:
    guide = _guide()
    payload = guide.model_dump(mode="json")
    payload["generation_metadata"] = None

    polished, _ = polish_learning_guide_with_llm(
        guide,
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        provider_router=FakeRouter(payload),
    )

    assert polished.generation_metadata is not None
    assert polished.generation_metadata.sections[0].section_name == "Key Vocabulary"


def test_polisher_invalid_schema_raises_clear_error() -> None:
    guide = _guide()

    with pytest.raises(Exception, match="LearningGuide schema"):
        polish_learning_guide_with_llm(
            guide,
            source_language="French",
            explanation_language="English",
            learner_level="A2",
            provider_router=FakeRouter({"title": "Bad Guide", "key_vocabulary": ["not an object"]}),
        )


def test_section_polisher_returns_valid_section_items() -> None:
    vocabulary = _guide().key_vocabulary

    polished, metadata = polish_key_vocabulary_with_llm(
        vocabulary,
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        provider_router=FakeRouter(
            {
                "key_vocabulary": [
                    {
                        "term": "la melodie",
                        "translation": "melody",
                        "part_of_speech": "noun",
                        "note": "Polished for workbook use.",
                    }
                ]
            }
        ),
    )

    assert polished[0].term == "la melodie"
    assert metadata.section_name == "Polish key vocabulary"


def test_section_polisher_invalid_schema_raises_clear_error() -> None:
    with pytest.raises(Exception, match="key_vocabulary"):
        polish_key_vocabulary_with_llm(
            _guide().key_vocabulary,
            source_language="French",
            explanation_language="English",
            learner_level="A2",
            provider_router=FakeRouter({"key_vocabulary": ["not an object"]}),
        )

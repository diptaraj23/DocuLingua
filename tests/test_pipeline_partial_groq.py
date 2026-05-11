from pathlib import Path

import pytest

from app.core.pipeline import generate_partial_groq_learning_guide_pdf
from app.llm.providers.metadata import GenerationAttempt, SectionGenerationMetadata


def test_partial_groq_pipeline_without_groq_creates_pdf(tmp_path: Path) -> None:
    result = generate_partial_groq_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_groq=False,
    )

    assert result["pdf_path"].exists()
    assert result["groq_sections_generated"] == []
    assert result["failed_groq_sections"] == []
    assert result["used_mock_fallback_sections"] == []
    assert result["process_steps"]
    assert result["total_duration_seconds"] >= 0


def test_partial_groq_pipeline_returns_compatibility_keys(tmp_path: Path) -> None:
    result = generate_partial_groq_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_groq=False,
    )

    assert "groq_sections_generated" in result
    assert "llm_sections_generated" in result
    assert "generation_metadata" in result
    assert "process_steps" in result
    assert "total_duration_seconds" in result


class FakeRouter:
    def __init__(self, fail_sections: set[str] | None = None) -> None:
        self.fail_sections = fail_sections or set()

    def generate_validated_json_with_fallback(self, prompt, section_name, validator, **kwargs):
        if section_name in self.fail_sections:
            raise ValueError(f"{section_name} failed")
        payload = _payload_for(section_name)
        metadata = SectionGenerationMetadata(
            section_name=section_name,
            provider="groq",
            model="test-model",
            success=True,
            attempts=[
                GenerationAttempt(
                    provider="groq",
                    model="test-model",
                    section_name=section_name,
                    success=True,
                )
            ],
        )
        return validator(payload), metadata


def test_partial_groq_pipeline_with_fake_router_creates_pdf(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter())

    result = generate_partial_groq_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_groq=True,
    )

    assert result["pdf_path"].exists()
    assert result["groq_sections_generated"] == [
        "Document Context Overview",
        "Key Vocabulary",
        "Important Verbs",
        "Grammar Patterns",
        "Useful Phrases and Expressions",
        "Mini Language Lessons",
        "Practice Exercises",
        "Short Reading Practice",
        "Review Sheet",
        "Answer Key",
    ]
    assert result["guide"].generation_metadata.sections[0].provider == "groq"
    assert any(row["status"] == "completed" for row in result["process_steps"])


def test_partial_groq_pipeline_falls_back_when_section_fails(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter({"Key Vocabulary"}))

    result = generate_partial_groq_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_groq=True,
    )

    assert result["pdf_path"].exists()
    assert "Key Vocabulary" in result["failed_groq_sections"]
    assert "Key Vocabulary" in result["used_mock_fallback_sections"]


def test_partial_groq_pipeline_raises_when_fallback_disabled(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter({"Key Vocabulary"}))

    with pytest.raises(ValueError, match="Key Vocabulary"):
        generate_partial_groq_learning_guide_pdf(
            file_path=Path("data/sample_documents/sample_french_text.txt"),
            source_language="French",
            explanation_language="English",
            learner_level="A2",
            output_dir=tmp_path,
            use_groq=True,
            fallback_to_mock_on_section_error=False,
        )


def _payload_for(section_name: str) -> dict:
    payloads = {
        "Document Context Overview": {
            "summary": "Generated overview.",
            "estimated_level": "A2",
            "difficulty_notes": "Friendly test content.",
            "main_learning_focus": ["vocabulary"],
            "suggested_study_approach": ["read and review"],
        },
        "Key Vocabulary": {
            "key_vocabulary": [
                {
                    "word": "la musique",
                    "meaning": "music",
                    "part_of_speech": "noun",
                    "why_useful": "Useful topic word.",
                }
            ]
        },
        "Important Verbs": {
            "important_verbs": [
                {"verb": "jouer", "meaning": "to play", "common_form": "joue", "learning_note": "Useful."}
            ]
        },
        "Grammar Patterns": {
            "grammar_patterns": [
                {
                    "title": "Present tense",
                    "explanation": "Used for facts.",
                    "examples": ["Le rythme organise la musique."],
                    "learning_note": "Useful.",
                }
            ]
        },
        "Useful Phrases and Expressions": {
            "useful_phrases": [
                {"phrase": "par exemple", "meaning": "for example", "usage_note": "Useful for explanations."}
            ]
        },
        "Mini Language Lessons": {
            "mini_lessons": [
                {
                    "title": "Explain a concept",
                    "objective": "Define a term.",
                    "explanation": "Use simple present tense.",
                    "examples": ["Le rythme est important."],
                }
            ]
        },
        "Practice Exercises": {
            "practice_exercises": [
                {"instruction": "Fill the blank.", "question": "Je ___ la musique.", "answer": "joue"}
            ]
        },
        "Short Reading Practice": {
            "reading_practice": {
                "title": "Music",
                "passage": "Je joue de la musique.",
                "vocabulary_help": ["jouer = to play"],
                "questions": ["Que fait la personne?"],
                "answers": ["Elle joue de la musique."],
            }
        },
        "Review Sheet": {
            "review_sheet": {
                "top_vocabulary": ["musique"],
                "top_verbs": ["jouer"],
                "top_phrases": ["par exemple"],
                "grammar_points": ["present tense"],
                "study_tips": ["Review aloud"],
            }
        },
        "Answer Key": {"answer_key": ["1. joue"]},
    }
    return payloads[section_name]

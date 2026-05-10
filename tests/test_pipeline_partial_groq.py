from pathlib import Path

import pytest

from app.core.pipeline import generate_partial_groq_learning_guide_pdf
from app.learning.content_schema import (
    DocumentOverview,
    GrammarPattern,
    MiniLesson,
    PracticeExercise,
    ReadingPractice,
    ReviewSheet,
    UsefulPhrase,
    VerbItem,
    VocabularyItem,
)


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


def test_partial_groq_pipeline_returns_groq_sections_key(tmp_path: Path) -> None:
    result = generate_partial_groq_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_groq=False,
    )

    assert "groq_sections_generated" in result


def test_partial_groq_pipeline_with_monkeypatched_groq_creates_pdf(monkeypatch, tmp_path: Path) -> None:
    def fake_overview(**kwargs) -> DocumentOverview:
        return DocumentOverview(
            summary="Generated overview.",
            estimated_level="A2",
            difficulty_notes="Friendly test content.",
            main_learning_focus=["vocabulary"],
            suggested_study_approach=["read and review"],
        )

    def fake_vocabulary(**kwargs) -> list[VocabularyItem]:
        return [
            VocabularyItem(
                term="la musique",
                translation="music",
                part_of_speech="noun",
                note="Useful topic word.",
            )
        ]

    def fake_verbs(**kwargs) -> list[VerbItem]:
        return [VerbItem(infinitive="jouer", translation="to play")]

    def fake_grammar(**kwargs) -> list[GrammarPattern]:
        return [GrammarPattern(name="Test grammar", explanation="A useful pattern.")]

    def fake_phrases(**kwargs) -> list[UsefulPhrase]:
        return [UsefulPhrase(phrase="test phrase", translation="test meaning")]

    def fake_lessons(**kwargs) -> list[MiniLesson]:
        return [MiniLesson(title="Test lesson", explanation="A short lesson.")]

    def fake_exercises(**kwargs) -> list[PracticeExercise]:
        return [PracticeExercise(title="Exercise", questions=["Q"], answers=["A"])]

    def fake_reading(**kwargs) -> ReadingPractice:
        return ReadingPractice(passage="Je joue.", questions=["Q"], answers=["A"])

    def fake_review(**kwargs) -> ReviewSheet:
        return ReviewSheet(key_points=["Review"], vocabulary_to_review=["musique"])

    def fake_answer_key(**kwargs) -> list[str]:
        return ["1. A"]

    monkeypatch.setattr("app.core.pipeline.generate_overview_with_groq", fake_overview)
    monkeypatch.setattr("app.core.pipeline.generate_key_vocabulary_with_groq", fake_vocabulary)
    monkeypatch.setattr("app.core.pipeline.generate_important_verbs_with_groq", fake_verbs)
    monkeypatch.setattr("app.core.pipeline.generate_grammar_patterns_with_groq", fake_grammar)
    monkeypatch.setattr("app.core.pipeline.generate_useful_phrases_with_groq", fake_phrases)
    monkeypatch.setattr("app.core.pipeline.generate_mini_lessons_with_groq", fake_lessons)
    monkeypatch.setattr("app.core.pipeline.generate_practice_exercises_with_groq", fake_exercises)
    monkeypatch.setattr("app.core.pipeline.generate_reading_practice_with_groq", fake_reading)
    monkeypatch.setattr("app.core.pipeline.generate_review_sheet_with_groq", fake_review)
    monkeypatch.setattr("app.core.pipeline.generate_answer_key_with_groq", fake_answer_key)

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


def test_partial_groq_pipeline_raises_when_a_groq_section_fails(monkeypatch, tmp_path: Path) -> None:
    def fake_overview(**kwargs) -> DocumentOverview:
        return DocumentOverview(summary="Generated overview.")

    def fake_vocabulary(**kwargs) -> list[VocabularyItem]:
        raise ValueError("No usable vocabulary")

    monkeypatch.setattr("app.core.pipeline.generate_overview_with_groq", fake_overview)
    monkeypatch.setattr("app.core.pipeline.generate_key_vocabulary_with_groq", fake_vocabulary)

    with pytest.raises(ValueError, match="Groq section generation failed"):
        generate_partial_groq_learning_guide_pdf(
            file_path=Path("data/sample_documents/sample_french_text.txt"),
            source_language="French",
            explanation_language="English",
            learner_level="A2",
            output_dir=tmp_path,
            use_groq=True,
        )

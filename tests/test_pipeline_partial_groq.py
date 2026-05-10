from pathlib import Path

from app.core.pipeline import generate_partial_groq_learning_guide_pdf
from app.learning.content_schema import DocumentOverview, VocabularyItem


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

    monkeypatch.setattr("app.core.pipeline.generate_overview_with_groq", fake_overview)
    monkeypatch.setattr("app.core.pipeline.generate_key_vocabulary_with_groq", fake_vocabulary)

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
    ]


def test_partial_groq_pipeline_falls_back_when_vocabulary_fails(monkeypatch, tmp_path: Path) -> None:
    def fake_overview(**kwargs) -> DocumentOverview:
        return DocumentOverview(summary="Generated overview.")

    def fake_vocabulary(**kwargs) -> list[VocabularyItem]:
        raise ValueError("No usable vocabulary")

    monkeypatch.setattr("app.core.pipeline.generate_overview_with_groq", fake_overview)
    monkeypatch.setattr("app.core.pipeline.generate_key_vocabulary_with_groq", fake_vocabulary)

    result = generate_partial_groq_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_groq=True,
    )

    assert result["pdf_path"].exists()
    assert result["groq_sections_generated"] == ["Document Context Overview"]
    assert result["guide"].key_vocabulary

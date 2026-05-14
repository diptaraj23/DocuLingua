from pathlib import Path

import pytest

from app.core.pipeline import generate_llm_learning_guide_pdf
from app.learning.content_schema import LearningGuide

from tests.test_pipeline_partial_groq import FakeRouter


def test_pipeline_without_polisher_works(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter())

    result = generate_llm_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_llm=True,
        polish_final_guide=False,
    )

    assert result["pdf_path"].exists()
    assert result["polishing_succeeded"] is False


def test_pipeline_polisher_uses_polished_guide(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter())

    result = generate_llm_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_llm=True,
        polish_final_guide=True,
    )

    assert result["guide"].key_vocabulary[0].term == "la melodie"
    assert result["polishing_succeeded"] is True
    assert "Polish key vocabulary" in result["llm_sections_generated"]


def test_pipeline_polisher_failure_falls_back_to_unpolished(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter())

    def failing_polisher(*args, **kwargs):
        raise ValueError("polish failed")

    monkeypatch.setattr("app.core.pipeline.polish_key_vocabulary_with_llm", failing_polisher)

    result = generate_llm_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_llm=True,
        polish_final_guide=True,
    )

    assert result["pdf_path"].exists()
    assert "Polish key vocabulary" in result["used_unpolished_fallback_sections"]


def test_pipeline_polisher_failure_raises_when_fallback_disabled(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter())

    def failing_polisher(*args, **kwargs):
        raise ValueError("polish failed")

    monkeypatch.setattr("app.core.pipeline.polish_key_vocabulary_with_llm", failing_polisher)

    with pytest.raises(ValueError, match="polish failed"):
        generate_llm_learning_guide_pdf(
            file_path=Path("data/sample_documents/sample_french_text.txt"),
            source_language="French",
            explanation_language="English",
            learner_level="A2",
            output_dir=tmp_path,
            use_llm=True,
            polish_final_guide=True,
            fallback_to_unpolished_on_polish_error=False,
        )


def test_pipeline_process_steps_include_polisher(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("app.core.pipeline.ProviderRouter", lambda: FakeRouter())

    result = generate_llm_learning_guide_pdf(
        file_path=Path("data/sample_documents/sample_french_text.txt"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
        use_llm=False,
    )

    assert any(row["step"] == "Polish key vocabulary" for row in result["process_steps"])

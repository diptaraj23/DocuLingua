from pathlib import Path

from app.core.pipeline import generate_mock_learning_guide_pdf


def test_generate_mock_learning_guide_pdf_creates_pdf(tmp_path: Path) -> None:
    sample = Path("data/sample_documents/sample_french_text.txt")

    result = generate_mock_learning_guide_pdf(
        file_path=sample,
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        output_dir=tmp_path,
    )

    assert result["pdf_path"].exists()
    assert result["guide"].key_vocabulary
    assert result["chunks"]

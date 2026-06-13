import fitz

from app.learning.mock_guide_generator import create_mock_learning_guide
from app.llm.providers.metadata import GenerationAttempt, GuideGenerationMetadata, SectionGenerationMetadata
from app.pdf.pdf_builder import _write_pymupdf_fallback_pdf, build_learning_guide_pdf

def test_pdf_generation_creates_non_empty_file_wesyprint(tmp_path) -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )
    pdf_path, model = build_learning_guide_pdf(guide, tmp_path / "guide.pdf")

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert model == "WeasyPrint"

def test_pdf_generation_creates_non_empty_file(tmp_path) -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )
    pdf_path, model = build_learning_guide_pdf(guide, tmp_path / "guide.pdf")

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert model == "WeasyPrint" or model == "PyMuPDF"


def test_pymupdf_pdf_contains_workbook_structure_and_compact_metadata(tmp_path) -> None:
    guide = create_mock_learning_guide(
        clean_text="Le rythme organise la musique.",
        stats={"word_count": 5, "paragraph_count": 1},
    )
    guide.generation_metadata = GuideGenerationMetadata(
        sections=[
            SectionGenerationMetadata(
                section_name="Key Vocabulary",
                provider="groq",
                model="test-model",
                success=True,
                attempts=[
                    GenerationAttempt(
                        provider="groq",
                        model="test-model",
                        section_name="Key Vocabulary",
                        success=True,
                    )
                ],
            )
        ]
    )
    pdf_path = tmp_path / "fallback.pdf"

    _write_pymupdf_fallback_pdf(pdf_path, guide)
    text = "\n".join(page.get_text() for page in fitz.open(pdf_path))

    assert pdf_path.exists()
    assert "Table of Contents" in text
    assert "1. Document Context Overview" in text
    assert "2. Key Vocabulary" in text
    assert "Generation Information" in text
    assert "Key Vocabulary" in text
    assert "test-model" in text


def test_pymupdf_answer_key_does_not_append_reading_answers(tmp_path) -> None:
    guide = create_mock_learning_guide(
        clean_text="Le rythme organise la musique.",
        stats={"word_count": 5, "paragraph_count": 1},
        answer_key=["Exercise 1: La"],
    )
    pdf_path = tmp_path / "fallback.pdf"

    _write_pymupdf_fallback_pdf(pdf_path, guide)
    text = "\n".join(page.get_text() for page in fitz.open(pdf_path))

    assert "Exercise 1: La" in text
    assert "Reading Practice:" not in text

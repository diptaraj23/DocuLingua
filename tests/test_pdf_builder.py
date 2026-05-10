from app.learning.mock_guide_generator import create_mock_learning_guide
from app.pdf.pdf_builder import build_learning_guide_pdf, render_learning_guide_html


def test_html_rendering_contains_major_section_titles() -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )

    html = render_learning_guide_html(guide)

    assert "Document Context Overview" in html
    assert "Key Vocabulary" in html
    assert "Answer Key" in html


def test_pdf_generation_creates_non_empty_file(tmp_path) -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )
    pdf_path = build_learning_guide_pdf(guide, tmp_path / "guide.pdf")

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0

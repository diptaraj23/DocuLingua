from app.learning.content_schema import LearningGuide
from app.pdf.pdf_builder import render_learning_guide_pdf


def test_learning_guide_schema_can_be_created() -> None:
    guide = LearningGuide(title="Test Guide")

    assert guide.title == "Test Guide"
    assert guide.source_language == "French"


def test_pdf_builder_imports() -> None:
    assert callable(render_learning_guide_pdf)

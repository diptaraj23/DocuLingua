"""High-level placeholder pipeline for generating learning guides."""

from __future__ import annotations

from pathlib import Path

from app.core.document_loader import load_document
from app.core.text_chunker import chunk_text
from app.core.text_cleaner import clean_text
from app.core.text_stats import get_text_statistics
from app.learning.content_schema import DocumentOverview, LearningGuide
from app.learning.groq_guide_generator import (
    generate_grammar_patterns_with_groq,
    generate_key_vocabulary_with_groq,
    generate_mini_lessons_with_groq,
    generate_overview_with_groq,
    generate_useful_phrases_with_groq,
)
from app.learning.mock_guide_generator import create_mock_learning_guide
from app.pdf.pdf_builder import build_learning_guide_pdf


def process_document_for_preview(file_path: Path) -> dict:
    """Load, clean, chunk, and summarize a document for Streamlit preview."""

    raw_text = load_document(Path(file_path))
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text)
    stats = get_text_statistics(cleaned_text)

    return {
        "raw_text": raw_text,
        "clean_text": cleaned_text,
        "chunks": chunks,
        "stats": stats,
    }


def generate_mock_learning_guide_pdf(
    file_path: Path,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    output_dir: Path,
) -> dict:
    """Create a mock LearningGuide and render it to a static PDF."""

    processed = process_document_for_preview(file_path)
    guide = create_mock_learning_guide(
        clean_text=processed["clean_text"],
        stats=processed["stats"],
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )

    output_path = Path(output_dir) / f"{Path(file_path).stem}_sample_learning_guide.pdf"
    pdf_path = build_learning_guide_pdf(guide, output_path)

    return {
        "guide": guide,
        "pdf_path": pdf_path,
        "stats": processed["stats"],
        "chunks": processed["chunks"],
    }


def generate_partial_groq_learning_guide_pdf(
    file_path: Path,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    output_dir: Path,
    use_groq: bool = True,
) -> dict:
    """Generate a PDF with selected Groq sections and mock remaining sections."""

    processed = process_document_for_preview(file_path)
    clean_text_for_groq = processed["clean_text"][:12000]
    # Future work can process larger documents chunk-by-chunk; this MVP sends a safe truncation.
    overview = None
    key_vocabulary = None
    grammar_patterns = None
    useful_phrases = None
    mini_lessons = None
    groq_sections_generated: list[str] = []

    if use_groq:
        try:
            overview = generate_overview_with_groq(
                clean_text=clean_text_for_groq,
                stats=processed["stats"],
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
            )
            groq_sections_generated.append("Document Context Overview")

            key_vocabulary = generate_key_vocabulary_with_groq(
                clean_text=clean_text_for_groq,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
            )
            groq_sections_generated.append("Key Vocabulary")

            grammar_patterns = generate_grammar_patterns_with_groq(
                clean_text=clean_text_for_groq,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
            )
            groq_sections_generated.append("Grammar Patterns")

            useful_phrases = generate_useful_phrases_with_groq(
                clean_text=clean_text_for_groq,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
            )
            groq_sections_generated.append("Useful Phrases and Expressions")

            mini_lessons = generate_mini_lessons_with_groq(
                clean_text=clean_text_for_groq,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
            )
            groq_sections_generated.append("Mini Language Lessons")
        except ValueError as error:
            raise ValueError(f"Groq section generation failed: {error}") from error

    guide = create_mock_learning_guide(
        clean_text=processed["clean_text"],
        stats=processed["stats"],
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        overview=overview,
        key_vocabulary=key_vocabulary,
        grammar_patterns=grammar_patterns,
        useful_phrases=useful_phrases,
        mini_lessons=mini_lessons,
    )

    suffix = "groq_sample_learning_guide" if use_groq else "sample_learning_guide"
    output_path = Path(output_dir) / f"{Path(file_path).stem}_{suffix}.pdf"
    pdf_path = build_learning_guide_pdf(guide, output_path)

    return {
        "guide": guide,
        "pdf_path": pdf_path,
        "stats": processed["stats"],
        "chunks": processed["chunks"],
        "groq_sections_generated": groq_sections_generated,
    }


def generate_learning_guide(
    document_path: str | Path,
    source_language: str = "French",
    explanation_language: str = "English",
    learner_level: str = "Intermediate",
) -> LearningGuide:
    """Create a placeholder learning guide from an uploaded document.

    Future phases will send cleaned chunks to Groq, parse structured responses,
    enrich them with vocabulary and grammar modules, and render a PDF.
    """

    processed = process_document_for_preview(Path(document_path))
    cleaned_text = processed["clean_text"]
    chunks = processed["chunks"]

    return LearningGuide(
        title="DocuLingua Learning Guide",
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        overview=DocumentOverview(
            summary="Placeholder summary generated from the uploaded document.",
            estimated_level=learner_level,
            main_learning_focus=["Vocabulary, useful phrases, and grammar patterns."],
            suggested_study_approach=[
                "Read the overview, study the vocabulary, then complete the exercises."
            ],
        ),
    )

"""High-level placeholder pipeline for generating learning guides."""

from __future__ import annotations

from pathlib import Path

from app.core.document_loader import load_document
from app.core.text_chunker import chunk_text
from app.core.text_cleaner import clean_text
from app.learning.content_schema import DocumentOverview, LearningGuide


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

    raw_text = load_document(document_path)
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text)

    return LearningGuide(
        title="DocuLingua Learning Guide",
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        overview=DocumentOverview(
            summary="Placeholder summary generated from the uploaded document.",
            estimated_difficulty=learner_level,
            main_learning_focus="Vocabulary, useful phrases, and grammar patterns.",
            suggested_study_approach="Read the overview, study the vocabulary, then complete the exercises.",
            document_chunk_count=len(chunks),
        ),
    )

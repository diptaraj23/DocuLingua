"""High-level placeholder pipeline for generating learning guides."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.core.document_loader import load_document
from app.core.progress_tracker import ProgressTracker
from app.core.text_chunker import chunk_text
from app.core.text_cleaner import clean_text
from app.core.text_stats import get_text_statistics
from app.learning.content_schema import DocumentOverview, LearningGuide
from app.learning.llm_guide_generator import (
    generate_answer_key_with_llm,
    generate_grammar_patterns_with_llm,
    generate_important_verbs_with_llm,
    generate_key_vocabulary_with_llm,
    generate_mini_lessons_with_llm,
    generate_overview_with_llm,
    generate_practice_exercises_with_llm,
    generate_reading_practice_with_llm,
    generate_review_sheet_with_llm,
    generate_useful_phrases_with_llm,
)
from app.llm.providers.metadata import GuideGenerationMetadata, SectionGenerationMetadata
from app.llm.providers.router import ProviderRouter
from app.learning.mock_guide_generator import create_mock_learning_guide
from app.pdf.pdf_builder import build_learning_guide_pdf
from app.utils.logging_utils import get_logger

MAX_LLM_INPUT_CHARS = 12000
MAX_GROQ_INPUT_CHARS = MAX_LLM_INPUT_CHARS
logger = get_logger(__name__)

PIPELINE_STEP_NAMES = [
    "Extract document text",
    "Clean text",
    "Chunk text",
    "Calculate document statistics",
    "Generate document overview",
    "Generate key vocabulary",
    "Generate important verbs",
    "Generate grammar patterns",
    "Generate useful phrases",
    "Generate mini lessons",
    "Generate practice exercises",
    "Generate reading practice",
    "Generate review sheet",
    "Generate answer key",
    "Render PDF",
]


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


def _process_document_with_progress(
    file_path: Path,
    progress_tracker: ProgressTracker,
    progress_callback: Callable[[ProgressTracker], None] | None = None,
) -> dict:
    """Load, clean, chunk, and summarize a document while updating progress."""

    def notify() -> None:
        if progress_callback:
            progress_callback(progress_tracker)

    extraction_model = "PyMuPDF" if Path(file_path).suffix.lower() == ".pdf" else "TXT Reader"

    progress_tracker.start_step("Extract document text")
    notify()
    try:
        raw_text = load_document(Path(file_path))
        progress_tracker.complete_step("Extract document text", provider="Local", model=extraction_model)
        notify()
    except Exception as error:
        progress_tracker.fail_step("Extract document text", str(error))
        notify()
        raise

    progress_tracker.start_step("Clean text")
    notify()
    cleaned_text = clean_text(raw_text)
    progress_tracker.complete_step("Clean text", provider="Local", model="Python")
    notify()

    progress_tracker.start_step("Chunk text")
    notify()
    chunks = chunk_text(cleaned_text)
    progress_tracker.complete_step("Chunk text", provider="Local", model="Python")
    notify()

    progress_tracker.start_step("Calculate document statistics")
    notify()
    stats = get_text_statistics(cleaned_text)
    progress_tracker.complete_step("Calculate document statistics", provider="Local", model="Python")
    notify()

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

    tracker = ProgressTracker(PIPELINE_STEP_NAMES)
    processed = _process_document_with_progress(file_path, tracker)
    guide = create_mock_learning_guide(
        clean_text=processed["clean_text"],
        stats=processed["stats"],
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )

    output_path = Path(output_dir) / f"{Path(file_path).stem}_sample_learning_guide.pdf"
    tracker.start_step("Render PDF")
    pdf_path = build_learning_guide_pdf(guide, output_path)
    tracker.complete_step("Render PDF", provider="Local", model="WeasyPrint/PyMuPDF")
    total_duration = sum(row["duration_seconds"] or 0 for row in tracker.get_display_rows())

    return {
        "guide": guide,
        "pdf_path": pdf_path,
        "stats": processed["stats"],
        "chunks": processed["chunks"],
        "process_steps": tracker.get_display_rows(),
        "total_duration_seconds": round(total_duration, 2),
    }


def generate_partial_groq_learning_guide_pdf(
    file_path: Path,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    output_dir: Path,
    use_groq: bool = True,
    fallback_to_mock_on_section_error: bool = True,
    progress_tracker: ProgressTracker | None = None,
    progress_callback: Callable[[ProgressTracker], None] | None = None,
) -> dict:
    """Backward-compatible wrapper for the provider-agnostic LLM pipeline."""

    return generate_llm_learning_guide_pdf(
        file_path=file_path,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        output_dir=output_dir,
        use_llm=use_groq,
        fallback_to_mock_on_section_error=fallback_to_mock_on_section_error,
        progress_tracker=progress_tracker,
        progress_callback=progress_callback,
    )


def generate_llm_learning_guide_pdf(
    file_path: Path,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    output_dir: Path,
    use_llm: bool = True,
    fallback_to_mock_on_section_error: bool = True,
    provider_router: ProviderRouter | None = None,
    progress_tracker: ProgressTracker | None = None,
    progress_callback: Callable[[ProgressTracker], None] | None = None,
) -> dict:
    """Generate a PDF using configured LLM providers with section-level fallback."""

    tracker = progress_tracker or ProgressTracker(PIPELINE_STEP_NAMES)

    def notify() -> None:
        if progress_callback:
            progress_callback(tracker)

    processed = _process_document_with_progress(file_path, tracker, progress_callback)
    clean_text_for_llm = processed["clean_text"][:MAX_LLM_INPUT_CHARS]
    # Future work can process larger documents chunk-by-chunk; this MVP sends a safe truncation.
    overview = None
    key_vocabulary = None
    important_verbs = None
    grammar_patterns = None
    useful_phrases = None
    mini_lessons = None
    practice_exercises = None
    reading_practice = None
    review_sheet = None
    answer_key = None
    llm_sections_generated: list[str] = []
    failed_llm_sections: list[str] = []
    used_mock_fallback_sections: list[str] = []
    section_metadata: list[SectionGenerationMetadata] = []
    router = provider_router or ProviderRouter()

    def run_section(section_name: str, step_name: str, generator):
        tracker.start_step(step_name)
        notify()
        try:
            value, metadata = generator()
        except Exception as error:
            logger.info("LLM section failed: %s: %s", section_name, error)
            failed_llm_sections.append(section_name)
            if fallback_to_mock_on_section_error:
                used_mock_fallback_sections.append(section_name)
                section_metadata.append(SectionGenerationMetadata(section_name=section_name))
                tracker.mark_fallback(step_name, str(error))
                notify()
                return None
            tracker.fail_step(step_name, str(error))
            notify()
            raise ValueError(f"LLM section generation failed for {section_name}: {error}") from error
        section_metadata.append(metadata)
        llm_sections_generated.append(section_name)
        tracker.complete_step(step_name, provider=metadata.provider, model=metadata.model)
        notify()
        return value

    def complete_mock_step(step_name: str) -> None:
        tracker.start_step(step_name)
        notify()
        tracker.complete_step(step_name, provider="Mock", model="Local sample content")
        notify()

    if use_llm:
        overview = run_section(
            "Document Context Overview",
            "Generate document overview",
            lambda: generate_overview_with_llm(
                clean_text=clean_text_for_llm,
                stats=processed["stats"],
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        key_vocabulary = run_section(
            "Key Vocabulary",
            "Generate key vocabulary",
            lambda: generate_key_vocabulary_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        important_verbs = run_section(
            "Important Verbs",
            "Generate important verbs",
            lambda: generate_important_verbs_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        grammar_patterns = run_section(
            "Grammar Patterns",
            "Generate grammar patterns",
            lambda: generate_grammar_patterns_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        useful_phrases = run_section(
            "Useful Phrases and Expressions",
            "Generate useful phrases",
            lambda: generate_useful_phrases_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        mini_lessons = run_section(
            "Mini Language Lessons",
            "Generate mini lessons",
            lambda: generate_mini_lessons_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        practice_exercises = run_section(
            "Practice Exercises",
            "Generate practice exercises",
            lambda: generate_practice_exercises_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        reading_practice = run_section(
            "Short Reading Practice",
            "Generate reading practice",
            lambda: generate_reading_practice_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        review_sheet = run_section(
            "Review Sheet",
            "Generate review sheet",
            lambda: generate_review_sheet_with_llm(
                clean_text=clean_text_for_llm,
                source_language=source_language,
                explanation_language=explanation_language,
                learner_level=learner_level,
                provider_router=router,
            ),
        )
        if practice_exercises is not None and reading_practice is not None:
            answer_key = run_section(
                "Answer Key",
                "Generate answer key",
                lambda: generate_answer_key_with_llm(
                    exercises=practice_exercises,
                    reading_practice=reading_practice,
                    source_language=source_language,
                    explanation_language=explanation_language,
                    provider_router=router,
                ),
            )
        elif fallback_to_mock_on_section_error:
            failed_llm_sections.append("Answer Key")
            used_mock_fallback_sections.append("Answer Key")
            section_metadata.append(SectionGenerationMetadata(section_name="Answer Key"))
            tracker.mark_fallback("Generate answer key", "Required prior sections failed.")
            notify()
        else:
            tracker.fail_step("Generate answer key", "Required prior sections failed.")
            notify()
            raise ValueError("LLM section generation failed for Answer Key: required prior sections failed.")
    else:
        for step_name in [
            "Generate document overview",
            "Generate key vocabulary",
            "Generate important verbs",
            "Generate grammar patterns",
            "Generate useful phrases",
            "Generate mini lessons",
            "Generate practice exercises",
            "Generate reading practice",
            "Generate review sheet",
            "Generate answer key",
        ]:
            complete_mock_step(step_name)

    guide = create_mock_learning_guide(
        clean_text=processed["clean_text"],
        stats=processed["stats"],
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        overview=overview,
        key_vocabulary=key_vocabulary,
        important_verbs=important_verbs,
        grammar_patterns=grammar_patterns,
        useful_phrases=useful_phrases,
        mini_lessons=mini_lessons,
        practice_exercises=practice_exercises,
        reading_practice=reading_practice,
        review_sheet=review_sheet,
        answer_key=answer_key,
    )
    guide.generation_metadata = GuideGenerationMetadata(sections=section_metadata)

    suffix = "llm_learning_guide" if use_llm else "sample_learning_guide"
    output_path = Path(output_dir) / f"{Path(file_path).stem}_{suffix}.pdf"
    tracker.start_step("Render PDF")
    notify()
    try:
        pdf_path = build_learning_guide_pdf(guide, output_path)
        tracker.complete_step("Render PDF", provider="Local", model="WeasyPrint/PyMuPDF")
        notify()
    except Exception as error:
        tracker.fail_step("Render PDF", str(error))
        notify()
        raise
    total_duration = sum(
        row["duration_seconds"] or 0
        for row in tracker.get_display_rows()
        if row["status"] in {"completed", "failed", "fallback"}
    )

    return {
        "guide": guide,
        "pdf_path": pdf_path,
        "stats": processed["stats"],
        "chunks": processed["chunks"],
        "llm_sections_generated": llm_sections_generated,
        "failed_llm_sections": failed_llm_sections,
        "generation_metadata": guide.generation_metadata,
        "process_steps": tracker.get_display_rows(),
        "total_duration_seconds": round(total_duration, 2),
        "groq_sections_generated": llm_sections_generated,
        "failed_groq_sections": failed_llm_sections,
        "used_mock_fallback_sections": used_mock_fallback_sections,
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

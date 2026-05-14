"""High-level placeholder pipeline for generating learning guides."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from app.core.document_loader import load_document
from app.core.progress_tracker import ProgressTracker
from app.core.text_chunker import chunk_text
from app.core.text_cleaner import clean_text
from app.core.text_stats import get_text_statistics
from app.learning.content_schema import DocumentOverview, LearningGuide, VocabularyGroup, VocabularyItem
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
from app.learning.guide_polisher import (
    SECTION_POLISH_STEPS,
    polish_answer_key_with_llm,
    polish_document_overview_with_llm,
    polish_grammar_patterns_with_llm,
    polish_important_verbs_with_llm,
    polish_key_vocabulary_with_llm,
    polish_mini_lessons_with_llm,
    polish_practice_exercises_with_llm,
    polish_reading_practice_with_llm,
    polish_review_sheet_with_llm,
    polish_useful_phrases_with_llm,
    polish_vocabulary_groups_with_llm,
)
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
    *SECTION_POLISH_STEPS,
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


def _derive_llm_guide_title(file_path: Path, overview: DocumentOverview | None, source_language: str) -> str:
    """Create a non-mock title for an LLM-generated guide."""

    stem = file_path.stem.replace("_", " ").replace("-", " ").strip()
    if stem:
        title = " ".join(word.capitalize() for word in stem.split())
    else:
        title = f"{source_language} Learning Guide"
    if overview and overview.estimated_level:
        return f"{title} - {source_language} Learning Guide"
    return title


def _derive_llm_topic(overview: DocumentOverview | None, key_vocabulary: list[VocabularyItem] | None) -> str:
    """Derive a concise topic label without falling back to mock sample text."""

    if overview and overview.main_learning_focus:
        focus = overview.main_learning_focus[0].strip()
        if focus:
            return focus
    if key_vocabulary:
        terms = [item.term for item in key_vocabulary[:3] if item.term]
        if terms:
            return ", ".join(terms)
    return "uploaded document context"


def _derive_vocabulary_groups(key_vocabulary: list[VocabularyItem] | None) -> list[VocabularyGroup] | None:
    """Create simple topic vocabulary groups from generated key vocabulary."""

    if not key_vocabulary:
        return None

    nouns = [item for item in key_vocabulary if "noun" in item.part_of_speech.lower()]
    verbs = [item for item in key_vocabulary if "verb" in item.part_of_speech.lower()]
    expressions = [
        item
        for item in key_vocabulary
        if item not in nouns
        and item not in verbs
        and ("expression" in item.part_of_speech.lower() or "phrase" in item.part_of_speech.lower())
    ]
    remaining = [item for item in key_vocabulary if item not in nouns and item not in verbs and item not in expressions]

    groups: list[VocabularyGroup] = []
    if nouns:
        groups.append(VocabularyGroup(topic="Key Nouns and Concepts", items=nouns[:8]))
    if verbs:
        groups.append(VocabularyGroup(topic="Useful Actions", items=verbs[:8]))
    if expressions:
        groups.append(VocabularyGroup(topic="Reusable Expressions", items=expressions[:8]))
    if remaining:
        groups.append(VocabularyGroup(topic="Document Topic Words", items=remaining[:8]))
    return groups or None


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
        tracker.start_step(step_name)
        tracker.complete_step(step_name, provider="Mock", model="Local sample content")
    for step_name in SECTION_POLISH_STEPS:
        tracker.start_step(step_name)
        tracker.complete_step(step_name, provider="Skipped", model="Polishing disabled")

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
    polish_final_guide: bool = False,
    fallback_to_unpolished_on_polish_error: bool = True,
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
        polish_final_guide=polish_final_guide,
        fallback_to_unpolished_on_polish_error=fallback_to_unpolished_on_polish_error,
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
    polish_final_guide: bool = False,
    fallback_to_unpolished_on_polish_error: bool = True,
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
    used_unpolished_fallback_sections: list[str] = []
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
        for step_name in SECTION_POLISH_STEPS:
            tracker.start_step(step_name)
            notify()
            tracker.complete_step(step_name, provider="Skipped", model="Polishing disabled")
            notify()

    guide = create_mock_learning_guide(
        clean_text=processed["clean_text"],
        stats=processed["stats"],
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        title=(
            _derive_llm_guide_title(Path(file_path), overview, source_language)
            if use_llm
            else None
        ),
        topic=(
            _derive_llm_topic(overview, key_vocabulary)
            if use_llm
            else None
        ),
        overview=overview,
        key_vocabulary=key_vocabulary,
        vocabulary_groups=(
            _derive_vocabulary_groups(key_vocabulary)
            if use_llm
            else None
        ),
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

    polishing_succeeded = False
    polishing_metadata: list[SectionGenerationMetadata] = []
    if polish_final_guide and use_llm:
        def run_polish(step_name: str, setter, generator) -> None:
            tracker.start_step(step_name)
            notify()
            try:
                value, metadata = generator()
            except Exception as error:
                logger.info("LLM polishing failed for %s: %s", step_name, error)
                failed_llm_sections.append(step_name)
                if fallback_to_unpolished_on_polish_error:
                    used_unpolished_fallback_sections.append(step_name)
                    tracker.mark_fallback(step_name, str(error))
                    notify()
                    return
                tracker.fail_step(step_name, str(error))
                notify()
                raise ValueError(f"LLM polishing failed for {step_name}: {error}") from error
            setter(value)
            polishing_metadata.append(metadata)
            section_metadata.append(metadata)
            llm_sections_generated.append(step_name)
            tracker.complete_step(step_name, provider=metadata.provider, model=metadata.model)
            notify()

        run_polish(
            "Polish document overview",
            lambda value: setattr(guide, "overview", value),
            lambda: polish_document_overview_with_llm(
                guide.overview, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish key vocabulary",
            lambda value: setattr(guide, "key_vocabulary", value),
            lambda: polish_key_vocabulary_with_llm(
                guide.key_vocabulary, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish topic vocabulary groups",
            lambda value: setattr(guide, "vocabulary_groups", value),
            lambda: polish_vocabulary_groups_with_llm(
                guide.vocabulary_groups, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish important verbs",
            lambda value: setattr(guide, "important_verbs", value),
            lambda: polish_important_verbs_with_llm(
                guide.important_verbs, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish grammar patterns",
            lambda value: setattr(guide, "grammar_patterns", value),
            lambda: polish_grammar_patterns_with_llm(
                guide.grammar_patterns, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish useful phrases",
            lambda value: setattr(guide, "useful_phrases", value),
            lambda: polish_useful_phrases_with_llm(
                guide.useful_phrases, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish mini lessons",
            lambda value: setattr(guide, "mini_lessons", value),
            lambda: polish_mini_lessons_with_llm(
                guide.mini_lessons, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish practice exercises",
            lambda value: setattr(guide, "practice_exercises", value),
            lambda: polish_practice_exercises_with_llm(
                guide.practice_exercises, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish reading practice",
            lambda value: setattr(guide, "reading_practice", value),
            lambda: polish_reading_practice_with_llm(
                guide.reading_practice, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish review sheet",
            lambda value: setattr(guide, "review_sheet", value),
            lambda: polish_review_sheet_with_llm(
                guide.review_sheet, source_language, explanation_language, learner_level, router
            ),
        )
        run_polish(
            "Polish answer key",
            lambda value: setattr(guide, "answer_key", value),
            lambda: polish_answer_key_with_llm(
                guide.answer_key, source_language, explanation_language, learner_level, router
            ),
        )
        polishing_succeeded = bool(polishing_metadata) and not used_unpolished_fallback_sections
        guide.generation_metadata = GuideGenerationMetadata(sections=section_metadata)
    elif use_llm:
        for step_name in SECTION_POLISH_STEPS:
            tracker.start_step(step_name)
            notify()
            tracker.complete_step(step_name, provider="Skipped", model="Polishing disabled")
            notify()

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
        "used_unpolished_fallback_sections": used_unpolished_fallback_sections,
        "polish_final_guide": polish_final_guide,
        "polishing_succeeded": polishing_succeeded,
        "polishing_metadata": polishing_metadata,
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

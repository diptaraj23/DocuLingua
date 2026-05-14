"""Provider-agnostic LLM adapters for LearningGuide section generation."""

from __future__ import annotations

from typing import Any

from app.llm.prompts import (
    build_answer_key_prompt,
    build_document_overview_prompt,
    build_grammar_patterns_prompt,
    build_important_verbs_prompt,
    build_key_vocabulary_prompt,
    build_mini_lessons_prompt,
    build_practice_exercises_prompt,
    build_reading_practice_prompt,
    build_review_sheet_prompt,
    build_useful_phrases_prompt,
)
from app.llm.providers.metadata import SectionGenerationMetadata
from app.llm.providers.router import ProviderRouter
from app.learning.content_schema import (
    DocumentOverview,
    GrammarPattern,
    LearningStatistics,
    MiniLesson,
    PracticeExercise,
    ReadingPractice,
    ReviewSheet,
    UsefulPhrase,
    VerbItem,
    VocabularyItem,
)
from app.learning.groq_guide_generator import (
    _answer_key_schema,
    _as_text,
    _as_text_list,
    _document_overview_schema,
    _find_list_or_mapping,
    _find_vocabulary_items,
    _grammar_patterns_from_raw,
    _grammar_patterns_schema,
    _important_verbs_schema,
    _key_vocabulary_schema,
    _mini_lessons_from_raw,
    _mini_lessons_schema,
    _practice_exercises_from_raw,
    _practice_exercises_schema,
    _reading_practice_schema,
    _review_sheet_schema,
    _useful_phrases_from_raw,
    _useful_phrases_schema,
    _verb_items_from_raw,
    _vocabulary_items_from_raw,
)


def generate_overview_with_llm(
    clean_text: str,
    stats: dict,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[DocumentOverview, SectionGenerationMetadata]:
    """Generate the document overview using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_document_overview_prompt(clean_text, stats, source_language, explanation_language, learner_level)

    def validator(data: dict[str, Any]) -> DocumentOverview:
        return DocumentOverview(
            summary=_as_text(data.get("summary"), "Overview generated from the document context."),
            estimated_level=_as_text(data.get("estimated_level"), learner_level),
            difficulty_notes=_as_text(data.get("difficulty_notes"), "Review vocabulary before rereading."),
            learning_statistics=LearningStatistics(),
            main_learning_focus=_as_text_list(data.get("main_learning_focus"), []),
            suggested_study_approach=_as_text_list(data.get("suggested_study_approach"), []),
        )

    return router.generate_validated_json_with_fallback(
        prompt,
        "Document Context Overview",
        validator,
        json_schema=_document_overview_schema(),
    )


def generate_key_vocabulary_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_words: int = 30,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[VocabularyItem], SectionGenerationMetadata]:
    """Generate key vocabulary using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_key_vocabulary_prompt(clean_text, source_language, explanation_language, learner_level, max_words)

    def validator(data: dict[str, Any]) -> list[VocabularyItem]:
        items = _vocabulary_items_from_raw(_find_vocabulary_items(data))
        if not items:
            raise ValueError("No usable vocabulary items.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Key Vocabulary",
        validator,
        json_schema=_key_vocabulary_schema(),
    )


def generate_important_verbs_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_verbs: int = 15,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[VerbItem], SectionGenerationMetadata]:
    """Generate important verbs using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_important_verbs_prompt(clean_text, source_language, explanation_language, learner_level, max_verbs)

    def validator(data: dict[str, Any]) -> list[VerbItem]:
        items = _verb_items_from_raw(_find_list_or_mapping(data, ["important_verbs", "verbs", "verbes", "items"]))
        if not items:
            raise ValueError("No usable important verbs.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Important Verbs",
        validator,
        json_schema=_important_verbs_schema(),
    )


def generate_grammar_patterns_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_patterns: int = 5,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[GrammarPattern], SectionGenerationMetadata]:
    """Generate grammar patterns using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_grammar_patterns_prompt(
        clean_text, source_language, explanation_language, learner_level, max_patterns
    )

    def validator(data: dict[str, Any]) -> list[GrammarPattern]:
        items = _grammar_patterns_from_raw(_find_list_or_mapping(data, ["grammar_patterns", "grammar", "patterns"]))
        if not items:
            raise ValueError("No usable grammar patterns.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Grammar Patterns",
        validator,
        json_schema=_grammar_patterns_schema(),
    )


def generate_useful_phrases_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_phrases: int = 15,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[UsefulPhrase], SectionGenerationMetadata]:
    """Generate useful phrases using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_useful_phrases_prompt(clean_text, source_language, explanation_language, learner_level, max_phrases)

    def validator(data: dict[str, Any]) -> list[UsefulPhrase]:
        items = _useful_phrases_from_raw(_find_list_or_mapping(data, ["useful_phrases", "phrases", "expressions"]))
        if not items:
            raise ValueError("No usable useful phrases.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Useful Phrases and Expressions",
        validator,
        json_schema=_useful_phrases_schema(),
    )


def generate_mini_lessons_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_lessons: int = 4,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[MiniLesson], SectionGenerationMetadata]:
    """Generate mini lessons using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_mini_lessons_prompt(clean_text, source_language, explanation_language, learner_level, max_lessons)

    def validator(data: dict[str, Any]) -> list[MiniLesson]:
        items = _mini_lessons_from_raw(_find_list_or_mapping(data, ["mini_lessons", "lessons", "language_lessons"]))
        if not items:
            raise ValueError("No usable mini lessons.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Mini Language Lessons",
        validator,
        json_schema=_mini_lessons_schema(),
    )


def generate_practice_exercises_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_exercises: int = 10,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[PracticeExercise], SectionGenerationMetadata]:
    """Generate practice exercises using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_practice_exercises_prompt(
        clean_text, source_language, explanation_language, learner_level, max_exercises
    )

    def validator(data: dict[str, Any]) -> list[PracticeExercise]:
        items = _practice_exercises_from_raw(
            _find_list_or_mapping(data, ["practice_exercises", "exercises", "exercices"])
        )
        if not items:
            raise ValueError("No usable practice exercises.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Practice Exercises",
        validator,
        json_schema=_practice_exercises_schema(),
    )


def generate_reading_practice_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[ReadingPractice, SectionGenerationMetadata]:
    """Generate reading practice using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_reading_practice_prompt(clean_text, source_language, explanation_language, learner_level)

    def validator(data: dict[str, Any]) -> ReadingPractice:
        raw = data.get("reading_practice", data)
        if not isinstance(raw, dict) or not _as_text(raw.get("passage"), ""):
            raise ValueError("Reading practice passage is missing.")
        return ReadingPractice(
            passage=_as_text(raw.get("passage"), ""),
            questions=_as_text_list(raw.get("questions"), []),
            answers=_as_text_list(raw.get("answers"), []),
        )

    return router.generate_validated_json_with_fallback(
        prompt,
        "Short Reading Practice",
        validator,
        json_schema=_reading_practice_schema(),
    )


def generate_review_sheet_with_llm(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[ReviewSheet, SectionGenerationMetadata]:
    """Generate review sheet using the configured provider router."""

    router = provider_router or ProviderRouter()
    prompt = build_review_sheet_prompt(clean_text, source_language, explanation_language, learner_level)

    def validator(data: dict[str, Any]) -> ReviewSheet:
        raw = data.get("review_sheet", data)
        if not isinstance(raw, dict):
            raise ValueError("Review sheet object is missing.")
        vocabulary = _as_text_list(raw.get("top_vocabulary"), [])
        verbs = _as_text_list(raw.get("top_verbs"), [])
        phrases = _as_text_list(raw.get("top_phrases"), [])
        grammar = _as_text_list(raw.get("grammar_points"), [])
        tips = _as_text_list(raw.get("study_tips"), [])
        if not any([vocabulary, verbs, phrases, grammar, tips]):
            raise ValueError("Review sheet did not include usable items.")
        key_points = []
        if vocabulary:
            key_points.append("Review the core vocabulary: " + ", ".join(vocabulary[:8]))
        if verbs:
            key_points.append("Practice the main verbs: " + ", ".join(verbs[:6]))
        if phrases:
            key_points.append("Reuse these phrases in your own sentences: " + ", ".join(phrases[:5]))
        if grammar:
            key_points.append("Connect the grammar points to examples from the document.")
        return ReviewSheet(
            key_points=key_points,
            vocabulary_to_review=vocabulary,
            grammar_to_review=grammar,
            study_plan=tips,
        )

    return router.generate_validated_json_with_fallback(
        prompt,
        "Review Sheet",
        validator,
        json_schema=_review_sheet_schema(),
    )


def generate_answer_key_with_llm(
    exercises: list[PracticeExercise],
    reading_practice: ReadingPractice,
    source_language: str,
    explanation_language: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[str], SectionGenerationMetadata]:
    """Generate an answer key using the configured provider router."""

    router = provider_router or ProviderRouter()
    exercise_payload = [{"title": exercise.title, "answers": exercise.answers} for exercise in exercises]
    reading_payload = {"questions": reading_practice.questions, "answers": reading_practice.answers}
    prompt = build_answer_key_prompt(exercise_payload, reading_payload, source_language, explanation_language)

    def validator(data: dict[str, Any]) -> list[str]:
        items = _dedupe_answer_key(_as_text_list(data.get("answer_key"), []))
        if not items:
            raise ValueError("Answer key list is missing.")
        return items

    return router.generate_validated_json_with_fallback(
        prompt,
        "Answer Key",
        validator,
        json_schema=_answer_key_schema(),
    )


def _dedupe_answer_key(items: list[str]) -> list[str]:
    """Remove exact duplicate answer-key lines while preserving order."""

    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        normalized = " ".join(item.lower().split())
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(item)
    return deduped

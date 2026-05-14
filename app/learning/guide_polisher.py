"""Final LLM-powered polishing pass for learning guide sections."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter, ValidationError

from app.learning.content_schema import (
    DocumentOverview,
    GrammarPattern,
    LearningGuide,
    MiniLesson,
    PracticeExercise,
    ReadingPractice,
    ReviewSheet,
    UsefulPhrase,
    VerbItem,
    VocabularyGroup,
    VocabularyItem,
)
from app.llm.prompts import build_learning_guide_polisher_prompt, build_section_polisher_prompt
from app.llm.providers.exceptions import LLMValidationError
from app.llm.providers.metadata import GuideGenerationMetadata, SectionGenerationMetadata
from app.llm.providers.router import ProviderRouter


SECTION_POLISH_STEPS = [
    "Polish document overview",
    "Polish key vocabulary",
    "Polish topic vocabulary groups",
    "Polish important verbs",
    "Polish grammar patterns",
    "Polish useful phrases",
    "Polish mini lessons",
    "Polish practice exercises",
    "Polish reading practice",
    "Polish review sheet",
    "Polish answer key",
]


def polish_document_overview_with_llm(
    overview: DocumentOverview,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[DocumentOverview, SectionGenerationMetadata]:
    """Polish the document overview section."""

    return _polish_model_section(
        section_key="overview",
        section_name="Polish document overview",
        value=overview,
        adapter=TypeAdapter(DocumentOverview),
        expected_json_shape={"overview": _shape_from_model(overview)},
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_key_vocabulary_with_llm(
    vocabulary: list[VocabularyItem],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[VocabularyItem], SectionGenerationMetadata]:
    """Polish the key vocabulary section."""

    return _polish_list_section(
        section_key="key_vocabulary",
        section_name="Polish key vocabulary",
        value=vocabulary,
        adapter=TypeAdapter(list[VocabularyItem]),
        expected_item=_shape_from_model(VocabularyItem(term="...", translation="...")),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_vocabulary_groups_with_llm(
    vocabulary_groups: list[VocabularyGroup],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[VocabularyGroup], SectionGenerationMetadata]:
    """Polish topic-based vocabulary groups."""

    return _polish_list_section(
        section_key="vocabulary_groups",
        section_name="Polish topic vocabulary groups",
        value=vocabulary_groups,
        adapter=TypeAdapter(list[VocabularyGroup]),
        expected_item=_shape_from_model(VocabularyGroup(topic="...", items=[VocabularyItem(term="...")])),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_important_verbs_with_llm(
    verbs: list[VerbItem],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[VerbItem], SectionGenerationMetadata]:
    """Polish important verbs."""

    return _polish_list_section(
        section_key="important_verbs",
        section_name="Polish important verbs",
        value=verbs,
        adapter=TypeAdapter(list[VerbItem]),
        expected_item=_shape_from_model(VerbItem(infinitive="...", translation="...")),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_grammar_patterns_with_llm(
    patterns: list[GrammarPattern],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[GrammarPattern], SectionGenerationMetadata]:
    """Polish grammar patterns."""

    return _polish_list_section(
        section_key="grammar_patterns",
        section_name="Polish grammar patterns",
        value=patterns,
        adapter=TypeAdapter(list[GrammarPattern]),
        expected_item=_shape_from_model(GrammarPattern(name="...", explanation="...")),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_useful_phrases_with_llm(
    phrases: list[UsefulPhrase],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[UsefulPhrase], SectionGenerationMetadata]:
    """Polish useful phrases and expressions."""

    return _polish_list_section(
        section_key="useful_phrases",
        section_name="Polish useful phrases",
        value=phrases,
        adapter=TypeAdapter(list[UsefulPhrase]),
        expected_item=_shape_from_model(UsefulPhrase(phrase="...", translation="...")),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_mini_lessons_with_llm(
    lessons: list[MiniLesson],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[MiniLesson], SectionGenerationMetadata]:
    """Polish mini lessons."""

    return _polish_list_section(
        section_key="mini_lessons",
        section_name="Polish mini lessons",
        value=lessons,
        adapter=TypeAdapter(list[MiniLesson]),
        expected_item=_shape_from_model(MiniLesson(title="...", explanation="...")),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_practice_exercises_with_llm(
    exercises: list[PracticeExercise],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[PracticeExercise], SectionGenerationMetadata]:
    """Polish practice exercises."""

    return _polish_list_section(
        section_key="practice_exercises",
        section_name="Polish practice exercises",
        value=exercises,
        adapter=TypeAdapter(list[PracticeExercise]),
        expected_item=_shape_from_model(PracticeExercise(title="...", questions=["..."], answers=["..."])),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_reading_practice_with_llm(
    reading_practice: ReadingPractice,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[ReadingPractice, SectionGenerationMetadata]:
    """Polish the reading practice section."""

    return _polish_model_section(
        section_key="reading_practice",
        section_name="Polish reading practice",
        value=reading_practice,
        adapter=TypeAdapter(ReadingPractice),
        expected_json_shape={"reading_practice": _shape_from_model(reading_practice)},
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_review_sheet_with_llm(
    review_sheet: ReviewSheet,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[ReviewSheet, SectionGenerationMetadata]:
    """Polish the review sheet."""

    return _polish_model_section(
        section_key="review_sheet",
        section_name="Polish review sheet",
        value=review_sheet,
        adapter=TypeAdapter(ReviewSheet),
        expected_json_shape={"review_sheet": _shape_from_model(review_sheet)},
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_answer_key_with_llm(
    answer_key: list[str],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[list[str], SectionGenerationMetadata]:
    """Polish the answer key."""

    return _polish_list_section(
        section_key="answer_key",
        section_name="Polish answer key",
        value=answer_key,
        adapter=TypeAdapter(list[str]),
        expected_item="...",
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def polish_learning_guide_with_llm(
    guide: LearningGuide,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None = None,
) -> tuple[LearningGuide, SectionGenerationMetadata]:
    """Legacy whole-guide polisher kept for compatibility with older tests/imports."""

    router = provider_router or ProviderRouter()
    original_metadata = guide.generation_metadata
    guide_payload = _compact_guide_for_polishing(guide)
    prompt = build_learning_guide_polisher_prompt(
        guide_json=guide_payload,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )

    def validator(payload: dict[str, Any]) -> LearningGuide:
        try:
            polished = LearningGuide.model_validate(payload)
        except ValidationError as error:
            raise LLMValidationError(f"Polished guide did not match LearningGuide schema: {error}") from error
        if polished.generation_metadata is None:
            polished.generation_metadata = original_metadata
        return polished

    polished_guide, metadata = router.generate_validated_json_with_fallback(
        prompt=prompt,
        section_name="Polish learning guide",
        validator=validator,
        max_tokens=3500,
    )
    if polished_guide.generation_metadata is None:
        polished_guide.generation_metadata = original_metadata
    return polished_guide, metadata


def _polish_model_section(
    section_key: str,
    section_name: str,
    value,
    adapter: TypeAdapter,
    expected_json_shape: dict[str, Any],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None,
):
    payload = {section_key: value.model_dump(mode="json")}
    return _polish_section_payload(
        section_key=section_key,
        section_name=section_name,
        payload=payload,
        adapter=adapter,
        expected_json_shape=expected_json_shape,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def _polish_list_section(
    section_key: str,
    section_name: str,
    value: list,
    adapter: TypeAdapter,
    expected_item,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None,
):
    payload = {section_key: _dump_list(value)}
    return _polish_section_payload(
        section_key=section_key,
        section_name=section_name,
        payload=payload,
        adapter=adapter,
        expected_json_shape={section_key: [expected_item]},
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        provider_router=provider_router,
    )


def _polish_section_payload(
    section_key: str,
    section_name: str,
    payload: dict[str, Any],
    adapter: TypeAdapter,
    expected_json_shape: dict[str, Any],
    source_language: str,
    explanation_language: str,
    learner_level: str,
    provider_router: ProviderRouter | None,
):
    router = provider_router or ProviderRouter()
    prompt = build_section_polisher_prompt(
        section_name=section_name,
        section_json=payload,
        expected_json_shape=expected_json_shape,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )

    def validator(response: dict[str, Any]):
        if section_key not in response:
            raise LLMValidationError(f"Polished section is missing `{section_key}`.")
        try:
            return adapter.validate_python(response[section_key])
        except ValidationError as error:
            raise LLMValidationError(f"Polished section did not match `{section_key}` schema: {error}") from error

    return router.generate_validated_json_with_fallback(
        prompt=prompt,
        section_name=section_name,
        validator=validator,
        max_tokens=1800,
    )


def _shape_from_model(value) -> dict[str, Any]:
    return value.model_dump(mode="json")


def _dump_list(values: list) -> list:
    dumped: list[Any] = []
    for item in values:
        dumped.append(item.model_dump(mode="json") if hasattr(item, "model_dump") else item)
    return dumped


def _compact_guide_for_polishing(guide: LearningGuide) -> dict[str, Any]:
    """Return a compact full-guide payload for the legacy whole-guide polisher."""

    payload = guide.model_dump(mode="json", exclude={"generation_metadata"})
    payload["overview"] = _compact_mapping(payload.get("overview", {}), max_chars=900)
    for key in [
        "key_vocabulary",
        "vocabulary_groups",
        "important_verbs",
        "grammar_patterns",
        "useful_phrases",
        "mini_lessons",
        "practice_exercises",
        "answer_key",
    ]:
        payload[key] = _compact_value(payload.get(key), max_chars=900)
    payload["reading_practice"] = _compact_mapping(payload.get("reading_practice", {}), max_chars=1200)
    payload["review_sheet"] = _compact_mapping(payload.get("review_sheet", {}), max_chars=900)
    return payload


def _compact_mapping(value: Any, max_chars: int) -> Any:
    if not isinstance(value, dict):
        return value
    return {key: _compact_value(item, max_chars=max_chars) for key, item in value.items()}


def _compact_value(value: Any, max_chars: int) -> Any:
    if isinstance(value, str):
        return value[:max_chars].strip()
    if isinstance(value, list):
        return [_compact_value(item, max_chars=max_chars) for item in value[:12]]
    if isinstance(value, dict):
        return _compact_mapping(value, max_chars=max_chars)
    return value


def metadata_for_polished_sections(sections: list[SectionGenerationMetadata]) -> GuideGenerationMetadata:
    """Build guide metadata from polishing section metadata."""

    return GuideGenerationMetadata(sections=sections)

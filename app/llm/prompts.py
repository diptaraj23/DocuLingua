"""Prompt builders backed by Markdown templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MAX_PROMPT_TEXT_CHARS = 8000
PROMPT_TEMPLATE_DIR = Path(__file__).parent / "prompt_templates"


class _SafeFormatDict(dict):
    """Return an empty string for missing optional template values."""

    def __missing__(self, key: str) -> str:
        return ""


def _truncate_text(clean_text: str, max_chars: int = MAX_PROMPT_TEXT_CHARS) -> str:
    """Limit prompt input size for MVP-friendly provider usage."""

    return clean_text[:max_chars].strip()


def _render_template(template_name: str, **values: Any) -> str:
    """Render a Markdown prompt template with simple Python formatting."""

    template_path = PROMPT_TEMPLATE_DIR / template_name
    template = template_path.read_text(encoding="utf-8")
    return template.format_map(_SafeFormatDict(values)).strip()


def build_document_overview_prompt(
    clean_text: str,
    stats: dict,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for the document overview section."""

    return _render_template(
        "document_overview.md",
        text=_truncate_text(clean_text),
        stats=stats,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )


def build_key_vocabulary_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_words: int = 30,
) -> str:
    """Build a JSON-only prompt for the key vocabulary section."""

    return _render_template(
        "key_vocabulary.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_words=max_words,
    )


def build_grammar_patterns_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_patterns: int = 5,
) -> str:
    """Build a JSON-only prompt for grammar patterns."""

    return _render_template(
        "grammar_patterns.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_patterns=max_patterns,
    )


def build_useful_phrases_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_phrases: int = 15,
) -> str:
    """Build a JSON-only prompt for useful phrases and expressions."""

    return _render_template(
        "useful_phrases.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_phrases=max_phrases,
    )


def build_mini_lessons_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_lessons: int = 4,
) -> str:
    """Build a JSON-only prompt for mini language lessons."""

    return _render_template(
        "mini_lessons.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_lessons=max_lessons,
    )


def build_important_verbs_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_verbs: int = 15,
) -> str:
    """Build a JSON-only prompt for important verbs."""

    return _render_template(
        "important_verbs.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_verbs=max_verbs,
    )


def build_practice_exercises_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_exercises: int = 10,
) -> str:
    """Build a JSON-only prompt for static practice exercises."""

    return _render_template(
        "practice_exercises.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_exercises=max_exercises,
    )


def build_reading_practice_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for reading practice."""

    return _render_template(
        "reading_practice.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )


def build_review_sheet_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for the review sheet."""

    return _render_template(
        "review_sheet.md",
        text=_truncate_text(clean_text),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )


def build_answer_key_prompt(
    exercises: list,
    reading_practice: dict,
    source_language: str,
    explanation_language: str,
) -> str:
    """Build a JSON-only prompt for the answer key."""

    return _render_template(
        "answer_key.md",
        exercises=exercises,
        reading_practice=reading_practice,
        source_language=source_language,
        explanation_language=explanation_language,
    )


def build_learning_guide_polisher_prompt(
    guide_json: dict,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for the final learning material polishing pass."""

    return _render_template(
        "learning_guide_polisher.md",
        guide_json=json.dumps(guide_json, ensure_ascii=False, indent=2),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )


def build_section_polisher_prompt(
    section_name: str,
    section_json: dict | list,
    expected_json_shape: dict | list,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for polishing one guide section."""

    return _render_template(
        "section_polisher.md",
        section_name=section_name,
        section_json=json.dumps(section_json, ensure_ascii=False, indent=2),
        expected_json_shape=json.dumps(expected_json_shape, ensure_ascii=False, indent=2),
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )


GRAMMAR_PROMPT = """
Identify useful grammar patterns in the document for the learner's level.
"""

MINI_LESSON_PROMPT = """
Create short mini lessons connected to the document topic and vocabulary.
"""

EXERCISE_PROMPT = """
Create static practice exercises suitable for a printable learning guide.
"""

REVIEW_SHEET_PROMPT = """
Create a concise review sheet and answer key for the generated learning guide.
"""

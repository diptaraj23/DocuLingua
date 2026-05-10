"""Adapters from Groq JSON responses to LearningGuide schema models."""

from __future__ import annotations

from typing import Any

from app.llm.groq_client import GroqClient
from app.llm.prompts import build_document_overview_prompt, build_key_vocabulary_prompt
from app.learning.content_schema import (
    DocumentOverview,
    LearningStatistics,
    VocabularyItem,
)


def generate_overview_with_groq(
    clean_text: str,
    stats: dict,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    groq_client: GroqClient | None = None,
) -> DocumentOverview:
    """Generate the document overview section with Groq."""

    client = groq_client or GroqClient()
    prompt = build_document_overview_prompt(
        clean_text=clean_text,
        stats=stats,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
    )
    data = client.generate_json(prompt)

    return DocumentOverview(
        summary=_as_text(data.get("summary"), "Overview will be generated from the document context."),
        estimated_level=_as_text(data.get("estimated_level"), learner_level),
        difficulty_notes=_as_text(
            data.get("difficulty_notes"),
            "Review the vocabulary and grammar patterns before rereading the document.",
        ),
        learning_statistics=LearningStatistics(),
        main_learning_focus=_as_text_list(
            data.get("main_learning_focus"),
            ["Document topic, reusable vocabulary, and grammar patterns."],
        ),
        suggested_study_approach=_as_text_list(
            data.get("suggested_study_approach"),
            ["Study the vocabulary first, then read the document again."],
        ),
    )


def generate_key_vocabulary_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_words: int = 30,
    groq_client: GroqClient | None = None,
) -> list[VocabularyItem]:
    """Generate key vocabulary items with Groq."""

    client = groq_client or GroqClient()
    prompt = build_key_vocabulary_prompt(
        clean_text=clean_text,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_words=max_words,
    )
    data = client.generate_json(prompt)
    raw_items = _find_vocabulary_items(data)
    if not isinstance(raw_items, list):
        raise ValueError("Groq vocabulary response did not include a valid key_vocabulary list.")

    vocabulary: list[VocabularyItem] = []
    for item in raw_items:
        if isinstance(item, str):
            parsed_item = _parse_vocabulary_string(item)
            if parsed_item is not None:
                vocabulary.append(parsed_item)
            continue
        if not isinstance(item, dict):
            continue
        word = _first_text(
            item,
            [
                "word",
                "term",
                "terme",
                "mot",
                "mot_francais",
                "source_word",
                "source",
                "french",
                "francais",
                "français",
                "vocabulary",
                "expression",
                "phrase",
                "concept",
                "Concept",
            ],
        )
        meaning = _first_text(
            item,
            [
                "meaning",
                "translation",
                "traduction",
                "english",
                "anglais",
                "definition",
                "définition",
                "definition_simple",
                "définition simple",
                "Définition simple",
                "explanation",
                "gloss",
            ],
        )
        if word and not meaning:
            meaning = _meaning_from_remaining_fields(item, word)
        if not word or not meaning:
            continue
        vocabulary.append(
            VocabularyItem(
                term=word,
                translation=meaning,
                part_of_speech=_first_text(
                    item,
                    ["part_of_speech", "pos", "type", "nature", "catégorie", "categorie"],
                ),
                note=_first_text(
                    item,
                    [
                        "why_useful",
                        "note",
                        "usage_note",
                        "why",
                        "usefulness",
                        "pourquoi_utile",
                        "utilité",
                        "utilite",
                    ],
                ),
            )
        )

    if not vocabulary:
        raise ValueError("Groq did not return any usable vocabulary items.")
    return vocabulary


def _as_text(value: Any, fallback: str) -> str:
    """Return a stripped string or fallback."""

    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _first_text(item: dict[str, Any], keys: list[str], fallback: str = "") -> str:
    """Return the first non-empty text value from possible response keys."""

    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def _find_vocabulary_items(data: dict[str, Any]) -> Any:
    """Find vocabulary items from common Groq response shapes."""

    direct_keys = [
        "key_vocabulary",
        "vocabulaire_cle",
        "vocabulaire_clé",
        "vocabulary",
        "vocabulaire",
        "items",
        "éléments",
        "elements",
        "words",
        "mots",
        "terms",
        "termes",
        "vocabulary_items",
    ]
    for key in direct_keys:
        value = data.get(key)
        if isinstance(value, list):
            return value

    for value in data.values():
        if isinstance(value, dict):
            nested = _find_vocabulary_items(value)
            if isinstance(nested, list):
                return nested
        if isinstance(value, list) and any(isinstance(item, (dict, str)) for item in value):
            return value
    return []


def _meaning_from_remaining_fields(item: dict[str, Any], word: str) -> str:
    """Build a concise meaning from non-word fields when labels are unexpected."""

    ignored_values = {word}
    parts: list[str] = []
    for key, value in item.items():
        if not isinstance(value, str):
            continue
        cleaned = value.strip()
        if not cleaned or cleaned in ignored_values:
            continue
        if key.lower() in {"example", "exemple"}:
            continue
        parts.append(cleaned)
    return " ".join(parts[:2])


def _parse_vocabulary_string(item: str) -> VocabularyItem | None:
    """Parse simple string vocabulary items like 'mot - meaning'."""

    text = item.strip()
    if not text:
        return None
    for separator in [" - ", " – ", " — ", ": ", " | "]:
        if separator in text:
            term, meaning = text.split(separator, 1)
            term = term.strip(" -*:|")
            meaning = meaning.strip()
            if term and meaning:
                return VocabularyItem(term=term, translation=meaning)
    return None


def _as_text_list(value: Any, fallback: list[str]) -> list[str]:
    """Return a clean list of strings or fallback."""

    if not isinstance(value, list):
        return fallback
    cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return cleaned or fallback

"""Adapters from Groq JSON responses to LearningGuide schema models."""

from __future__ import annotations

import re
from typing import Any

from app.llm.groq_client import GroqClient
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
    vocabulary = _vocabulary_items_from_raw(raw_items)

    if not vocabulary:
        retry_prompt = _build_vocabulary_retry_prompt(
            clean_text=clean_text,
            source_language=source_language,
            explanation_language=explanation_language,
            learner_level=learner_level,
            max_words=max_words,
        )
        retry_data = client.generate_json(retry_prompt, temperature=0.0, max_tokens=1200)
        vocabulary = _vocabulary_items_from_raw(_find_vocabulary_items(retry_data))

    if not vocabulary:
        vocabulary = _fallback_vocabulary_from_text(clean_text, max_words=min(max_words, 12))

    if not vocabulary:
        raise ValueError("Groq did not return any usable vocabulary items.")
    return vocabulary


def _vocabulary_items_from_raw(raw_items: Any) -> list[VocabularyItem]:
    """Convert flexible raw vocabulary response items into schema objects."""

    if not isinstance(raw_items, list):
        return []

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

    return vocabulary


def generate_grammar_patterns_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_patterns: int = 5,
    groq_client: GroqClient | None = None,
) -> list[GrammarPattern]:
    """Generate grammar patterns with Groq."""

    client = groq_client or GroqClient()
    prompt = build_grammar_patterns_prompt(
        clean_text=clean_text,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_patterns=max_patterns,
    )
    data = client.generate_json(prompt)
    raw_items = _find_list_or_mapping(data, ["grammar_patterns", "grammar", "patterns", "items"])
    patterns = _grammar_patterns_from_raw(raw_items)

    if not patterns:
        retry_prompt = _build_grammar_retry_prompt(clean_text, source_language, explanation_language, learner_level)
        retry_data = client.generate_json(retry_prompt, temperature=0.0, max_tokens=1200)
        patterns = _grammar_patterns_from_raw(
            _find_list_or_mapping(retry_data, ["grammar_patterns", "grammar", "patterns", "items"])
        )

    if not patterns:
        patterns = _fallback_grammar_patterns(source_language)

    if not patterns:
        raise ValueError("Groq did not return any usable grammar patterns.")
    return patterns


def _grammar_patterns_from_raw(raw_items: Any) -> list[GrammarPattern]:
    """Convert flexible raw grammar response items into schema objects."""

    patterns: list[GrammarPattern] = []

    for item in raw_items:
        if isinstance(item, str):
            parsed = _parse_grammar_string(item)
            if parsed is not None:
                patterns.append(parsed)
            continue
        if not isinstance(item, dict):
            continue
        title = _first_text(item, ["title", "name", "pattern", "grammar_pattern", "concept", "Concept"])
        explanation = _first_text(
            item,
            ["explanation", "description", "meaning", "definition", "Définition simple", "rule"],
        )
        examples = _as_text_list(item.get("examples") or item.get("exemples"), [])
        note = _first_text(item, ["learning_note", "note", "usage_note", "why_useful", "utilité"])
        if not title or not explanation:
            continue
        patterns.append(
            GrammarPattern(
                name=title,
                explanation=f"{explanation} {note}".strip(),
                examples=examples,
            )
        )

    return patterns


def generate_useful_phrases_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_phrases: int = 15,
    groq_client: GroqClient | None = None,
) -> list[UsefulPhrase]:
    """Generate useful phrases and expressions with Groq."""

    client = groq_client or GroqClient()
    prompt = build_useful_phrases_prompt(
        clean_text=clean_text,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_phrases=max_phrases,
    )
    data = client.generate_json(prompt)
    raw_items = _find_list_or_mapping(data, ["useful_phrases", "phrases", "expressions", "items"])
    phrases = _useful_phrases_from_raw(raw_items)

    if not phrases:
        retry_data = client.generate_json(
            _build_phrases_retry_prompt(clean_text, source_language, explanation_language, learner_level),
            temperature=0.0,
            max_tokens=1200,
        )
        phrases = _useful_phrases_from_raw(
            _find_list_or_mapping(retry_data, ["useful_phrases", "phrases", "expressions", "items"])
        )

    if not phrases:
        phrases = _fallback_useful_phrases()

    if not phrases:
        raise ValueError("Groq did not return any usable useful phrases.")
    return phrases


def _useful_phrases_from_raw(raw_items: Any) -> list[UsefulPhrase]:
    """Convert flexible raw phrase response items into schema objects."""

    phrases: list[UsefulPhrase] = []

    for item in raw_items:
        if isinstance(item, str):
            parsed = _parse_phrase_string(item)
            if parsed is not None:
                phrases.append(parsed)
            continue
        if not isinstance(item, dict):
            continue
        phrase = _first_text(item, ["phrase", "expression", "text"])
        meaning = _first_text(item, ["meaning", "translation", "english", "explanation"])
        usage_note = _first_text(item, ["usage_note", "note", "use", "context"])
        if not phrase or not meaning:
            continue
        phrases.append(UsefulPhrase(phrase=phrase, translation=meaning, usage_note=usage_note))

    return phrases


def generate_mini_lessons_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_lessons: int = 4,
    groq_client: GroqClient | None = None,
) -> list[MiniLesson]:
    """Generate mini language lessons with Groq."""

    client = groq_client or GroqClient()
    prompt = build_mini_lessons_prompt(
        clean_text=clean_text,
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        max_lessons=max_lessons,
    )
    data = client.generate_json(prompt)
    raw_items = _find_list_or_mapping(data, ["mini_lessons", "lessons", "language_lessons", "items"])
    lessons = _mini_lessons_from_raw(raw_items)

    if not lessons:
        retry_data = client.generate_json(
            _build_lessons_retry_prompt(clean_text, source_language, explanation_language, learner_level),
            temperature=0.0,
            max_tokens=1400,
        )
        lessons = _mini_lessons_from_raw(
            _find_list_or_mapping(retry_data, ["mini_lessons", "lessons", "language_lessons", "items"])
        )

    if not lessons:
        lessons = _fallback_mini_lessons()

    if not lessons:
        raise ValueError("Groq did not return any usable mini lessons.")
    return lessons


def generate_important_verbs_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_verbs: int = 15,
    groq_client: GroqClient | None = None,
) -> list[VerbItem]:
    """Generate important verbs with Groq."""

    client = groq_client or GroqClient()
    data = client.generate_json(
        build_important_verbs_prompt(
            clean_text, source_language, explanation_language, learner_level, max_verbs
        )
    )
    verbs = _verb_items_from_raw(_find_list_or_mapping(data, ["important_verbs", "verbs", "verbes", "items"]))

    if not verbs:
        retry_data = client.generate_json(
            _build_verbs_retry_prompt(clean_text, source_language, explanation_language, learner_level),
            temperature=0.0,
            max_tokens=1200,
        )
        verbs = _verb_items_from_raw(
            _find_list_or_mapping(retry_data, ["important_verbs", "verbs", "verbes", "items"])
        )

    if not verbs:
        verbs = _fallback_verbs_from_text(clean_text, max_verbs=min(max_verbs, 10))

    if not verbs:
        raise ValueError("Groq did not return any usable important verbs.")
    return verbs


def _verb_items_from_raw(raw_items: Any) -> list[VerbItem]:
    """Convert flexible raw verb response items into schema objects."""

    verbs: list[VerbItem] = []
    for item in raw_items:
        if isinstance(item, str):
            parsed = _parse_verb_string(item)
            if parsed is not None:
                verbs.append(parsed)
            continue
        if not isinstance(item, dict):
            continue
        verb = _first_text(item, ["verb", "verbe", "infinitive", "infinitif", "word", "term", "mot"])
        meaning = _first_text(item, ["meaning", "translation", "traduction", "english", "anglais", "definition"])
        if verb and not meaning:
            meaning = _meaning_from_remaining_fields(item, verb)
        if not verb or not meaning:
            continue
        verbs.append(
            VerbItem(
                infinitive=verb,
                translation=meaning,
                tense_or_form=_first_text(item, ["common_form", "form", "forme", "tense", "temps"]),
                example_sentence=_first_text(item, ["learning_note", "note", "example", "exemple"]),
            )
        )
    return verbs


def generate_practice_exercises_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_exercises: int = 10,
    groq_client: GroqClient | None = None,
) -> list[PracticeExercise]:
    """Generate static practice exercises with Groq."""

    client = groq_client or GroqClient()
    data = client.generate_json(
        build_practice_exercises_prompt(
            clean_text, source_language, explanation_language, learner_level, max_exercises
        )
    )
    exercises = _practice_exercises_from_raw(
        _find_list_or_mapping(data, ["practice_exercises", "exercises", "exercices", "items"])
    )

    if not exercises:
        retry_data = client.generate_json(
            _build_exercises_retry_prompt(clean_text, source_language, explanation_language, learner_level),
            temperature=0.0,
            max_tokens=1400,
        )
        exercises = _practice_exercises_from_raw(
            _find_list_or_mapping(retry_data, ["practice_exercises", "exercises", "exercices", "items"])
        )

    if not exercises:
        exercises = _fallback_practice_exercises()

    if not exercises:
        raise ValueError("Groq did not return any usable practice exercises.")
    return exercises


def _practice_exercises_from_raw(raw_items: Any) -> list[PracticeExercise]:
    """Convert flexible raw exercise response items into schema objects."""

    exercises: list[PracticeExercise] = []
    for index, item in enumerate(raw_items, start=1):
        if isinstance(item, str):
            parsed = _parse_exercise_string(item, index)
            if parsed is not None:
                exercises.append(parsed)
            continue
        if not isinstance(item, dict):
            continue
        instruction = _first_text(
            item,
            ["instruction", "instructions", "consigne", "type", "exercise_type", "title"],
        )
        question = _first_text(
            item,
            ["question", "prompt", "task", "exercice", "exercise", "sentence", "phrase"],
        )
        answer = _first_text(
            item,
            ["answer", "solution", "correct_answer", "réponse", "reponse", "answers"],
        )
        if not answer and isinstance(item.get("answers"), list):
            answers = _as_text_list(item.get("answers"), [])
            answer = "; ".join(answers)
        if not instruction or not question or not answer:
            continue
        exercises.append(
            PracticeExercise(
                title=f"Exercise {index}",
                instructions=instruction,
                questions=[question],
                answers=[answer],
            )
        )
    return exercises


def generate_reading_practice_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    groq_client: GroqClient | None = None,
) -> ReadingPractice:
    """Generate short reading practice with Groq."""

    client = groq_client or GroqClient()
    data = client.generate_json(
        build_reading_practice_prompt(clean_text, source_language, explanation_language, learner_level)
    )
    raw = data.get("reading_practice", data)
    if not isinstance(raw, dict):
        raise ValueError("Groq reading practice response was unusable.")
    passage = _as_text(raw.get("passage"), "")
    if not passage:
        raise ValueError("Groq reading practice did not include a passage.")
    vocab_help = _as_text_list(raw.get("vocabulary_help"), [])
    return ReadingPractice(
        passage=passage,
        questions=_as_text_list(raw.get("questions"), []),
        answers=_as_text_list(raw.get("answers"), []),
    )


def generate_review_sheet_with_groq(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    groq_client: GroqClient | None = None,
) -> ReviewSheet:
    """Generate the review sheet with Groq."""

    client = groq_client or GroqClient()
    data = client.generate_json(
        build_review_sheet_prompt(clean_text, source_language, explanation_language, learner_level)
    )
    raw = data.get("review_sheet", data)
    if not isinstance(raw, dict):
        raise ValueError("Groq review sheet response was unusable.")
    vocabulary = _as_text_list(raw.get("top_vocabulary"), [])
    verbs = _as_text_list(raw.get("top_verbs"), [])
    phrases = _as_text_list(raw.get("top_phrases"), [])
    grammar = _as_text_list(raw.get("grammar_points"), [])
    tips = _as_text_list(raw.get("study_tips"), [])
    if not any([vocabulary, verbs, phrases, grammar, tips]):
        raise ValueError("Groq review sheet did not include usable review items.")
    return ReviewSheet(
        key_points=vocabulary + verbs + phrases,
        vocabulary_to_review=vocabulary,
        grammar_to_review=grammar,
        study_plan=tips,
    )


def generate_answer_key_with_groq(
    exercises: list[PracticeExercise],
    reading_practice: ReadingPractice,
    source_language: str,
    explanation_language: str,
    groq_client: GroqClient | None = None,
) -> list[str]:
    """Generate an answer key with Groq, falling back to local answers."""

    client = groq_client or GroqClient()
    exercise_payload = [
        {"title": exercise.title, "answers": exercise.answers} for exercise in exercises
    ]
    reading_payload = {
        "questions": reading_practice.questions,
        "answers": reading_practice.answers,
    }
    try:
        data = client.generate_json(
            build_answer_key_prompt(
                exercise_payload, reading_payload, source_language, explanation_language
            )
        )
        answer_key = _as_text_list(data.get("answer_key"), [])
        if answer_key:
            return answer_key
    except Exception:
        pass
    return _build_local_answer_key(exercises, reading_practice)


def _mini_lessons_from_raw(raw_items: Any) -> list[MiniLesson]:
    """Convert flexible raw mini lesson response items into schema objects."""

    lessons: list[MiniLesson] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue
        title = _first_text(item, ["title", "name"])
        objective = _first_text(item, ["objective", "goal", "learning_goal"])
        explanation = _first_text(item, ["explanation", "description"])
        examples = _as_text_list(item.get("examples"), [])
        if not title or not explanation:
            continue
        lessons.append(
            MiniLesson(
                title=title,
                explanation=f"Objective: {objective} {explanation}".strip(),
                examples=examples,
            )
        )

    return lessons


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

    if _looks_like_vocabulary_item(data):
        return [data]

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
        if isinstance(value, dict):
            if _looks_like_vocabulary_item(value):
                return [value]
            mapped = _vocabulary_mapping_to_items(value)
            if mapped:
                return mapped

    for value in data.values():
        if isinstance(value, dict):
            if _looks_like_vocabulary_item(value):
                return [value]
            mapped = _vocabulary_mapping_to_items(value)
            if mapped:
                return mapped
            nested = _find_vocabulary_items(value)
            if isinstance(nested, list):
                return nested
        if isinstance(value, list) and any(isinstance(item, (dict, str)) for item in value):
            return value
    return []


def _looks_like_vocabulary_item(item: dict[str, Any]) -> bool:
    """Return True when a dictionary appears to represent one vocabulary item."""

    word_keys = {
        "word",
        "term",
        "terme",
        "mot",
        "source_word",
        "french",
        "français",
        "francais",
        "phrase",
        "expression",
        "concept",
        "Concept",
    }
    meaning_keys = {
        "meaning",
        "translation",
        "traduction",
        "english",
        "anglais",
        "definition",
        "définition",
        "explanation",
        "gloss",
        "Définition simple",
    }
    keys = set(item)
    return bool(keys & word_keys) and bool(keys & meaning_keys)


def _vocabulary_mapping_to_items(value: dict[str, Any]) -> list[dict[str, str]]:
    """Convert mappings like {'accord': 'chord'} into item dictionaries."""

    items: list[dict[str, str]] = []
    for key, meaning in value.items():
        if not isinstance(key, str) or not isinstance(meaning, str):
            continue
        if key.lower() in {"summary", "notes", "title", "topic"}:
            continue
        key = key.strip()
        meaning = meaning.strip()
        if key and meaning:
            items.append({"word": key, "meaning": meaning})
    return items


def _find_list(data: dict[str, Any], keys: list[str]) -> list[Any]:
    """Find a list in a nested Groq response."""

    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
    for value in data.values():
        if isinstance(value, dict):
            nested = _find_list(value, keys)
            if nested:
                return nested
    return []


def _find_list_or_mapping(data: dict[str, Any], keys: list[str]) -> list[Any]:
    """Find a list or convert a simple mapping into list-shaped items."""

    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            mapped = _mapping_to_named_items(value)
            if mapped:
                return mapped
    for value in data.values():
        if isinstance(value, dict):
            nested = _find_list_or_mapping(value, keys)
            if nested:
                return nested
    mapped = _mapping_to_named_items(data)
    return mapped


def _mapping_to_named_items(value: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert mappings like {'Present tense': 'Used for facts'} into items."""

    items: list[dict[str, Any]] = []
    ignored = {"summary", "title", "topic", "estimated_level", "difficulty_notes"}
    for key, entry in value.items():
        if not isinstance(key, str) or key in ignored:
            continue
        if isinstance(entry, str):
            items.append({"title": key, "explanation": entry, "phrase": key, "meaning": entry})
        elif isinstance(entry, dict):
            item = {"title": key, "phrase": key}
            item.update(entry)
            items.append(item)
    return items


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


def _parse_grammar_string(item: str) -> GrammarPattern | None:
    """Parse simple grammar strings like 'pattern - explanation'."""

    text = item.strip()
    if not text:
        return None
    for separator in [" - ", " – ", " — ", ": ", " | "]:
        if separator in text:
            title, explanation = text.split(separator, 1)
            title = title.strip(" -*:|")
            explanation = explanation.strip()
            if title and explanation:
                return GrammarPattern(name=title, explanation=explanation)
    return None


def _parse_verb_string(item: str) -> VerbItem | None:
    """Parse simple verb strings like 'jouer - to play'."""

    text = item.strip()
    if not text:
        return None
    for separator in [" - ", " – ", " — ", ": ", " | "]:
        if separator in text:
            verb, meaning = text.split(separator, 1)
            verb = verb.strip(" -*:|")
            meaning = meaning.strip()
            if verb and meaning:
                return VerbItem(infinitive=verb, translation=meaning)
    return None


def _parse_exercise_string(item: str, index: int) -> PracticeExercise | None:
    """Parse simple exercise strings like 'Question - Answer'."""

    text = item.strip()
    if not text:
        return None
    for separator in [" - ", " – ", " — ", " | "]:
        if separator in text:
            question, answer = text.split(separator, 1)
            question = question.strip(" -*:|")
            answer = answer.strip()
            if question and answer:
                return PracticeExercise(
                    title=f"Exercise {index}",
                    instructions="Answer the prompt.",
                    questions=[question],
                    answers=[answer],
                )
    return None


def _build_vocabulary_retry_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_words: int,
) -> str:
    """Build a short retry prompt for vocabulary if the main response is malformed."""

    text = clean_text[:3000].strip()
    return f"""
Return exactly one JSON object and nothing else.
Create {min(max_words, 12)} useful {source_language} vocabulary items for a {learner_level} learner.
Do not translate sentence by sentence.
Use this exact shape:
{{
  "key_vocabulary": [
    {{"word": "term from document", "meaning": "short {explanation_language} meaning", "part_of_speech": "noun/verb/etc", "why_useful": "short note"}}
  ]
}}
Document:
{text}
""".strip()


def _build_grammar_retry_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a short retry prompt for grammar if the main response is malformed."""

    text = clean_text[:3000].strip()
    return f"""
Return exactly one JSON object and nothing else.
Create 3 useful grammar patterns for a {learner_level} learner from this {source_language} document.
Do not translate sentence by sentence.
Use this exact shape:
{{
  "grammar_patterns": [
    {{"title": "pattern name", "explanation": "short {explanation_language} explanation", "examples": ["short {source_language} example"], "learning_note": "short note"}}
  ]
}}
Document:
{text}
""".strip()


def _build_verbs_retry_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a short retry prompt for verbs if the main response is malformed."""

    text = clean_text[:3000].strip()
    return f"""
Return exactly one JSON object and nothing else.
Create 8 useful {source_language} verbs for a {learner_level} learner from this document.
Do not translate sentence by sentence.
Use this exact shape:
{{
  "important_verbs": [
    {{"verb": "infinitive", "meaning": "short {explanation_language} meaning", "common_form": "common form from the text if known", "learning_note": "short note"}}
  ]
}}
Document:
{text}
""".strip()


def _build_exercises_retry_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a short retry prompt for exercises if the main response is malformed."""

    text = clean_text[:3000].strip()
    return f"""
Return exactly one JSON object and nothing else.
Create 5 static PDF practice exercises for a {learner_level} learner.
Do not create interactive exercises. Do not translate sentence by sentence.
Use this exact shape:
{{
  "practice_exercises": [
    {{"instruction": "short instruction", "question": "single exercise prompt", "answer": "short answer"}}
  ]
}}
Document:
{text}
""".strip()


def _build_phrases_retry_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a short retry prompt for phrases if the main response is malformed."""

    text = clean_text[:3000].strip()
    return f"""
Return exactly one JSON object and nothing else.
Create 6 reusable {source_language} phrases for a {learner_level} learner from this document.
Do not translate sentence by sentence.
Use this exact shape:
{{"useful_phrases": [{{"phrase": "short phrase", "meaning": "short {explanation_language} meaning", "usage_note": "short note"}}]}}
Document:
{text}
""".strip()


def _build_lessons_retry_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a short retry prompt for mini lessons if the main response is malformed."""

    text = clean_text[:3000].strip()
    return f"""
Return exactly one JSON object and nothing else.
Create 2 short language mini lessons for a {learner_level} learner inspired by this {source_language} document.
Do not create exercises. Do not translate sentence by sentence.
Use this exact shape:
{{"mini_lessons": [{{"title": "lesson title", "objective": "short objective", "explanation": "short {explanation_language} explanation", "examples": ["short {source_language} example"]}}]}}
Document:
{text}
""".strip()


def _fallback_vocabulary_from_text(clean_text: str, max_words: int) -> list[VocabularyItem]:
    """Create a deterministic local fallback so PDF generation is not blocked."""

    words = re.findall(r"\b[\wÀ-ÿ'-]{4,}\b", clean_text, flags=re.UNICODE)
    stopwords = {
        "avec",
        "dans",
        "pour",
        "plus",
        "cette",
        "vous",
        "nous",
        "elle",
        "sont",
        "être",
        "avoir",
        "page",
        "exemple",
    }
    seen: set[str] = set()
    items: list[VocabularyItem] = []
    for word in words:
        normalized = word.lower().strip("'")
        if normalized in stopwords or normalized in seen:
            continue
        seen.add(normalized)
        items.append(
            VocabularyItem(
                term=word,
                translation="Review this word in context",
                part_of_speech="",
                note="Local fallback item because Groq returned an unusable vocabulary shape.",
            )
        )
        if len(items) >= max_words:
            break
    return items


def _fallback_verbs_from_text(clean_text: str, max_verbs: int) -> list[VerbItem]:
    """Create deterministic verb fallback items from likely French verb forms."""

    candidates = re.findall(r"\b[\wÀ-ÿ']{4,}\b", clean_text, flags=re.UNICODE)
    likely_endings = ("er", "ir", "re", "ez", "ent", "ons", "ait", "aient", "ant")
    seen: set[str] = set()
    verbs: list[VerbItem] = []
    for word in candidates:
        normalized = word.lower().strip("'")
        if normalized in seen or not normalized.endswith(likely_endings):
            continue
        seen.add(normalized)
        verbs.append(
            VerbItem(
                infinitive=word,
                translation="Review this verb in context",
                tense_or_form="",
                example_sentence="Local fallback item because Groq returned an unusable verb shape.",
            )
        )
        if len(verbs) >= max_verbs:
            break
    if verbs:
        return verbs
    return [
        VerbItem(
            infinitive="utiliser",
            translation="to use",
            example_sentence="Fallback verb for discussing the document topic.",
        )
    ]


def _fallback_practice_exercises() -> list[PracticeExercise]:
    """Create deterministic static exercise fallback items."""

    return [
        PracticeExercise(
            title="Exercise 1",
            instructions="Choose the best article.",
            questions=["___ musique est importante. (Le / La / Les)"],
            answers=["La"],
        ),
        PracticeExercise(
            title="Exercise 2",
            instructions="Complete the sentence with a useful verb.",
            questions=["Je ___ le document et je note le vocabulaire."],
            answers=["lis"],
        ),
    ]


def _fallback_grammar_patterns(source_language: str) -> list[GrammarPattern]:
    """Create deterministic grammar fallback items."""

    return [
        GrammarPattern(
            name="Present tense for explanations",
            explanation="Use the present tense to explain facts, definitions, and general ideas.",
            examples=[f"{source_language} example: Le rythme organise la musique."],
        ),
        GrammarPattern(
            name="Nouns with articles",
            explanation="Review how nouns usually appear with articles such as le, la, l', and les.",
            examples=["la melodie", "le rythme", "les notes"],
        ),
    ]


def _fallback_useful_phrases() -> list[UsefulPhrase]:
    """Create deterministic phrase fallback items."""

    return [
        UsefulPhrase(
            phrase="cela signifie",
            translation="this means",
            usage_note="Useful for explaining a concept.",
        ),
        UsefulPhrase(
            phrase="par exemple",
            translation="for example",
            usage_note="Useful when giving examples.",
        ),
    ]


def _fallback_mini_lessons() -> list[MiniLesson]:
    """Create deterministic mini lesson fallback items."""

    return [
        MiniLesson(
            title="Explain a concept simply",
            explanation="Objective: describe a key idea with a short present-tense sentence.",
            examples=["Le rythme organise la musique.", "La melodie donne une forme."],
        )
    ]


def _build_local_answer_key(
    exercises: list[PracticeExercise],
    reading_practice: ReadingPractice,
) -> list[str]:
    """Build a deterministic answer key from generated exercise data."""

    answers: list[str] = []
    for index, exercise in enumerate(exercises, start=1):
        joined = "; ".join(exercise.answers) if exercise.answers else "No answer provided."
        answers.append(f"{index}. {exercise.title}: {joined}")
    for index, answer in enumerate(reading_practice.answers, start=1):
        answers.append(f"Reading {index}: {answer}")
    return answers


def _parse_phrase_string(item: str) -> UsefulPhrase | None:
    """Parse simple string phrases like 'phrase - meaning'."""

    text = item.strip()
    if not text:
        return None
    for separator in [" - ", " – ", " — ", ": ", " | "]:
        if separator in text:
            phrase, meaning = text.split(separator, 1)
            phrase = phrase.strip(" -*:|")
            meaning = meaning.strip()
            if phrase and meaning:
                return UsefulPhrase(phrase=phrase, translation=meaning)
    return None


def _as_text_list(value: Any, fallback: list[str]) -> list[str]:
    """Return a clean list of strings or fallback."""

    if not isinstance(value, list):
        return fallback
    cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return cleaned or fallback

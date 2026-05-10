from app.llm.prompts import (
    build_document_overview_prompt,
    build_grammar_patterns_prompt,
    build_key_vocabulary_prompt,
    build_mini_lessons_prompt,
    build_useful_phrases_prompt,
)


def test_overview_prompt_requests_json_only() -> None:
    prompt = build_document_overview_prompt(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5},
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "return JSON only" in prompt
    assert "Do not translate sentence by sentence" in prompt


def test_vocabulary_prompt_contains_expected_json_fields() -> None:
    prompt = build_key_vocabulary_prompt(
        clean_text="La musique rappelle des souvenirs.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "key_vocabulary" in prompt
    assert "word" in prompt
    assert "meaning" in prompt
    assert "part_of_speech" in prompt
    assert "why_useful" in prompt
    assert "Do not translate sentence by sentence" in prompt


def test_grammar_prompt_requests_json_only_and_expected_fields() -> None:
    prompt = build_grammar_patterns_prompt(
        clean_text="La musique rappelle des souvenirs.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "return JSON only" in prompt
    assert "Do not translate sentence by sentence" in prompt
    assert "grammar_patterns" in prompt
    assert "title" in prompt
    assert "explanation" in prompt
    assert "examples" in prompt
    assert "learning_note" in prompt


def test_useful_phrases_prompt_requests_json_only_and_expected_fields() -> None:
    prompt = build_useful_phrases_prompt(
        clean_text="La musique rappelle des souvenirs.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "return JSON only" in prompt
    assert "sentence-by-sentence translation" in prompt
    assert "useful_phrases" in prompt
    assert "phrase" in prompt
    assert "meaning" in prompt
    assert "usage_note" in prompt


def test_mini_lessons_prompt_requests_json_only_and_expected_fields() -> None:
    prompt = build_mini_lessons_prompt(
        clean_text="La musique rappelle des souvenirs.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "return JSON only" in prompt
    assert "sentence-wise translation" in prompt
    assert "mini_lessons" in prompt
    assert "title" in prompt
    assert "objective" in prompt
    assert "explanation" in prompt
    assert "examples" in prompt

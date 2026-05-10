from app.llm.prompts import build_document_overview_prompt, build_key_vocabulary_prompt


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

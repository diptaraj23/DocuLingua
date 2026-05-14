from app.llm.prompts import build_learning_guide_polisher_prompt, build_section_polisher_prompt
from app.learning.mock_guide_generator import create_mock_learning_guide


def test_polisher_prompt_contains_safety_and_schema_instructions() -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )

    prompt = build_learning_guide_polisher_prompt(
        guide_json=guide.model_dump(mode="json"),
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "Return JSON only" in prompt
    assert "Preserve the same JSON schema" in prompt
    assert "Do not create sentence-wise translation" in prompt
    assert "title" in prompt
    assert "overview" in prompt
    assert "key_vocabulary" in prompt
    assert "answer_key" in prompt


def test_section_polisher_prompt_contains_section_contract() -> None:
    prompt = build_section_polisher_prompt(
        section_name="Polish key vocabulary",
        section_json={"key_vocabulary": [{"term": "la musique", "translation": "music"}]},
        expected_json_shape={"key_vocabulary": [{"term": "...", "translation": "..."}]},
        source_language="French",
        explanation_language="English",
        learner_level="A2",
    )

    assert "Return JSON only" in prompt
    assert "Preserve the exact section JSON shape" in prompt
    assert "Do not create sentence-wise translation" in prompt
    assert "Polish key vocabulary" in prompt
    assert "key_vocabulary" in prompt

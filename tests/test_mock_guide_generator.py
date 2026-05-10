from app.learning.content_schema import LearningGuide
from app.learning.mock_guide_generator import create_mock_learning_guide


def test_create_mock_learning_guide_returns_learning_guide() -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )

    assert isinstance(guide, LearningGuide)


def test_mock_learning_guide_contains_required_sections() -> None:
    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
    )

    assert guide.key_vocabulary
    assert guide.grammar_patterns
    assert guide.mini_lessons
    assert guide.practice_exercises
    assert guide.answer_key

from app.learning.content_schema import (
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


def test_mock_learning_guide_accepts_external_groq_sections() -> None:
    grammar = [GrammarPattern(name="Test grammar", explanation="A useful pattern.")]
    phrases = [UsefulPhrase(phrase="test phrase", translation="test meaning")]
    lessons = [MiniLesson(title="Test lesson", explanation="A short lesson.")]

    guide = create_mock_learning_guide(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5, "paragraph_count": 1},
        grammar_patterns=grammar,
        useful_phrases=phrases,
        mini_lessons=lessons,
    )

    assert guide.grammar_patterns == grammar
    assert guide.useful_phrases == phrases
    assert guide.mini_lessons == lessons


def test_mock_learning_guide_accepts_remaining_external_sections() -> None:
    verbs = [VerbItem(infinitive="jouer", translation="to play")]
    exercises = [PracticeExercise(title="Test", questions=["Q"], answers=["A"])]
    reading = ReadingPractice(passage="Je joue.", questions=["Q"], answers=["A"])
    review = ReviewSheet(key_points=["Review this"])
    answer_key = ["1. A"]

    guide = create_mock_learning_guide(
        clean_text="Je joue de la musique.",
        stats={"word_count": 5, "paragraph_count": 1},
        important_verbs=verbs,
        practice_exercises=exercises,
        reading_practice=reading,
        review_sheet=review,
        answer_key=answer_key,
    )

    assert guide.important_verbs == verbs
    assert guide.practice_exercises == exercises
    assert guide.reading_practice == reading
    assert guide.review_sheet == review
    assert guide.answer_key == answer_key


def test_learning_guide_accepts_external_title_topic_and_vocabulary_groups() -> None:
    groups = [
        VocabularyGroup(
            topic="Music Theory",
            items=[VocabularyItem(term="le rythme", translation="rhythm")],
        )
    ]

    guide = create_mock_learning_guide(
        clean_text="Le rythme organise la musique.",
        stats={"word_count": 5, "paragraph_count": 1},
        title="Music Fundamentals - French Learning Guide",
        topic="music fundamentals",
        vocabulary_groups=groups,
    )

    assert guide.title == "Music Fundamentals - French Learning Guide"
    assert guide.topic == "music fundamentals"
    assert guide.vocabulary_groups == groups

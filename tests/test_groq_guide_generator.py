from app.learning.content_schema import (
    DocumentOverview,
    GrammarPattern,
    MiniLesson,
    PracticeExercise,
    ReadingPractice,
    ReviewSheet,
    UsefulPhrase,
    VerbItem,
    VocabularyItem,
)
from app.learning.groq_guide_generator import (
    generate_answer_key_with_groq,
    generate_grammar_patterns_with_groq,
    generate_important_verbs_with_groq,
    generate_key_vocabulary_with_groq,
    generate_mini_lessons_with_groq,
    generate_overview_with_groq,
    generate_practice_exercises_with_groq,
    generate_reading_practice_with_groq,
    generate_review_sheet_with_groq,
    generate_useful_phrases_with_groq,
)


class FakeGroqClient:
    def __init__(self, response: dict) -> None:
        self.response = response

    def generate_json(self, prompt: str, **kwargs) -> dict:
        return self.response


def test_generate_overview_with_groq_returns_document_overview() -> None:
    client = FakeGroqClient(
        {
            "summary": "A short text about music and memory.",
            "estimated_level": "A2",
            "difficulty_notes": "Mostly familiar narrative language.",
            "main_learning_focus": ["memory vocabulary", "imperfect tense"],
            "suggested_study_approach": ["Review words", "Reread the text"],
        }
    )

    overview = generate_overview_with_groq(
        clean_text="La musique rappelle des souvenirs.",
        stats={"word_count": 5},
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert isinstance(overview, DocumentOverview)
    assert overview.summary
    assert overview.main_learning_focus


def test_generate_key_vocabulary_with_groq_returns_items() -> None:
    client = FakeGroqClient(
        {
            "key_vocabulary": [
                {
                    "word": "la musique",
                    "meaning": "music",
                    "part_of_speech": "noun",
                    "why_useful": "Central topic word.",
                }
            ]
        }
    )

    vocabulary = generate_key_vocabulary_with_groq(
        clean_text="La musique rappelle des souvenirs.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert vocabulary
    assert isinstance(vocabulary[0], VocabularyItem)
    assert vocabulary[0].term == "la musique"


def test_generate_key_vocabulary_with_groq_accepts_alternate_keys() -> None:
    client = FakeGroqClient(
        {
            "vocabulary": [
                {
                    "term": "le rythme",
                    "translation": "rhythm",
                    "pos": "noun",
                    "note": "Useful in music texts.",
                },
                {
                    "french": "jouer",
                    "english": "to play",
                    "type": "verb",
                    "usefulness": "Reusable action verb.",
                },
            ]
        }
    )

    vocabulary = generate_key_vocabulary_with_groq(
        clean_text="Le rythme aide a jouer de la musique.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert [item.term for item in vocabulary] == ["le rythme", "jouer"]
    assert vocabulary[0].translation == "rhythm"


def test_generate_key_vocabulary_with_groq_accepts_french_table_keys() -> None:
    client = FakeGroqClient(
        {
            "vocabulaire": [
                {
                    "Concept": "Portee",
                    "Définition simple": "Lignes et espaces ou les notes sont placees.",
                },
                "accord - combination of several notes",
            ]
        }
    )

    vocabulary = generate_key_vocabulary_with_groq(
        clean_text="La portee et les accords sont importants.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert vocabulary[0].term == "Portee"
    assert vocabulary[0].translation.startswith("Lignes")
    assert vocabulary[1].term == "accord"


def test_generate_key_vocabulary_with_groq_accepts_mapping_response() -> None:
    client = FakeGroqClient({"key_vocabulary": {"accord": "chord", "rythme": "rhythm"}})

    vocabulary = generate_key_vocabulary_with_groq(
        clean_text="Un accord donne le rythme.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert [item.term for item in vocabulary] == ["accord", "rythme"]


def test_generate_key_vocabulary_with_groq_uses_local_fallback_when_needed() -> None:
    client = FakeGroqClient({"unexpected": "shape"})

    vocabulary = generate_key_vocabulary_with_groq(
        clean_text="La melodie accompagne le rythme et la memoire musicale.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert vocabulary
    assert vocabulary[0].translation == "Review this word in context"


def test_generate_grammar_patterns_with_groq_returns_items() -> None:
    client = FakeGroqClient(
        {
            "grammar_patterns": [
                {
                    "title": "The imperfect tense",
                    "explanation": "Use it for background description.",
                    "examples": ["La musique jouait."],
                    "learning_note": "Useful for setting a scene.",
                }
            ]
        }
    )

    patterns = generate_grammar_patterns_with_groq(
        clean_text="La musique jouait doucement.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert patterns
    assert isinstance(patterns[0], GrammarPattern)


def test_generate_grammar_patterns_with_groq_accepts_mapping_response() -> None:
    client = FakeGroqClient({"grammar_patterns": {"Present tense": "Used to explain facts."}})

    patterns = generate_grammar_patterns_with_groq(
        clean_text="Le rythme organise la musique.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert patterns[0].name == "Present tense"


def test_generate_grammar_patterns_with_groq_uses_fallback_when_needed() -> None:
    client = FakeGroqClient({"unexpected": []})

    patterns = generate_grammar_patterns_with_groq(
        clean_text="Le rythme organise la musique.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert patterns
    assert patterns[0].name == "Present tense for explanations"


def test_generate_useful_phrases_with_groq_returns_items() -> None:
    client = FakeGroqClient(
        {
            "useful_phrases": [
                {
                    "phrase": "cela me rappelle",
                    "meaning": "it reminds me",
                    "usage_note": "Use it to discuss memories.",
                }
            ]
        }
    )

    phrases = generate_useful_phrases_with_groq(
        clean_text="Cela me rappelle une chanson.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert phrases
    assert isinstance(phrases[0], UsefulPhrase)


def test_generate_useful_phrases_with_groq_uses_fallback_when_needed() -> None:
    client = FakeGroqClient({"unexpected": []})

    phrases = generate_useful_phrases_with_groq(
        clean_text="Le rythme organise la musique.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert phrases
    assert phrases[0].phrase == "cela signifie"


def test_generate_mini_lessons_with_groq_returns_items() -> None:
    client = FakeGroqClient(
        {
            "mini_lessons": [
                {
                    "title": "Describe a memory",
                    "objective": "Talk about memories with simple verbs.",
                    "explanation": "Use rappeler with a noun or person.",
                    "examples": ["Cette chanson me rappelle Paris."],
                }
            ]
        }
    )

    lessons = generate_mini_lessons_with_groq(
        clean_text="Cette chanson me rappelle Paris.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert lessons
    assert isinstance(lessons[0], MiniLesson)


def test_generate_mini_lessons_with_groq_uses_fallback_when_needed() -> None:
    client = FakeGroqClient({"unexpected": []})

    lessons = generate_mini_lessons_with_groq(
        clean_text="Le rythme organise la musique.",
        source_language="French",
        explanation_language="English",
        learner_level="A2",
        groq_client=client,
    )

    assert lessons
    assert lessons[0].title == "Explain a concept simply"


def test_generate_important_verbs_with_groq_returns_items() -> None:
    client = FakeGroqClient({"important_verbs": [{"verb": "jouer", "meaning": "to play", "common_form": "joue", "learning_note": "Reusable verb."}]})

    verbs = generate_important_verbs_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert verbs and isinstance(verbs[0], VerbItem)


def test_generate_important_verbs_with_groq_accepts_mapping_response() -> None:
    client = FakeGroqClient({"important_verbs": {"jouer": "to play", "chanter": "to sing"}})

    verbs = generate_important_verbs_with_groq("jouer chanter", "French", "English", "A2", groq_client=client)

    assert [verb.infinitive for verb in verbs] == ["jouer", "chanter"]


def test_generate_important_verbs_with_groq_uses_fallback_when_needed() -> None:
    client = FakeGroqClient({"unexpected": []})

    verbs = generate_important_verbs_with_groq(
        "Ecoutez la musique et chanter doucement.",
        "French",
        "English",
        "A2",
        groq_client=client,
    )

    assert verbs
    assert verbs[0].translation == "Review this verb in context"


def test_generate_practice_exercises_with_groq_returns_items() -> None:
    client = FakeGroqClient({"practice_exercises": [{"instruction": "Fill the blank.", "question": "Je ___ de la musique.", "answer": "joue"}]})

    exercises = generate_practice_exercises_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert exercises and isinstance(exercises[0], PracticeExercise)


def test_generate_practice_exercises_cleans_nested_numbering() -> None:
    client = FakeGroqClient(
        {
            "practice_exercises": [
                {
                    "instruction": "Complete the sentences.",
                    "question": "1. 1. Le ___ organise la musique. 2. La ___ monte.",
                    "answer": "rythme; melodie",
                }
            ]
        }
    )

    exercises = generate_practice_exercises_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert exercises[0].questions[0] == "Le ___ organise la musique."
    assert exercises[0].questions[1] == "La ___ monte."


def test_generate_practice_exercises_with_groq_accepts_alternate_keys() -> None:
    client = FakeGroqClient(
        {
            "exercices": [
                {
                    "consigne": "Complete the sentence.",
                    "phrase": "Je ___ la musique.",
                    "réponse": "joue",
                }
            ]
        }
    )

    exercises = generate_practice_exercises_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert exercises
    assert exercises[0].answers == ["joue"]


def test_generate_practice_exercises_with_groq_uses_fallback_when_needed() -> None:
    client = FakeGroqClient({"unexpected": []})

    exercises = generate_practice_exercises_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert exercises
    assert exercises[0].answers == ["La"]


def test_generate_reading_practice_with_groq_returns_item() -> None:
    client = FakeGroqClient({"reading_practice": {"title": "Music", "passage": "Je joue de la musique.", "vocabulary_help": ["jouer = to play"], "questions": ["Que fait je?"], "answers": ["Je joue."]}})

    reading = generate_reading_practice_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert isinstance(reading, ReadingPractice)
    assert reading.passage


def test_generate_review_sheet_with_groq_returns_item() -> None:
    client = FakeGroqClient({"review_sheet": {"top_vocabulary": ["musique"], "top_verbs": ["jouer"], "top_phrases": ["par exemple"], "grammar_points": ["present tense"], "study_tips": ["Review aloud"]}})

    review = generate_review_sheet_with_groq("jouer", "French", "English", "A2", groq_client=client)

    assert isinstance(review, ReviewSheet)
    assert review.vocabulary_to_review
    assert review.key_points[0].startswith("Review the core vocabulary")


def test_generate_answer_key_with_groq_returns_list() -> None:
    client = FakeGroqClient({"answer_key": ["1. joue", "Reading 1. Je joue."]})
    exercises = [PracticeExercise(title="Exercise", answers=["joue"])]
    reading = ReadingPractice(answers=["Je joue."])

    answer_key = generate_answer_key_with_groq(exercises, reading, "French", "English", groq_client=client)

    assert answer_key
    assert isinstance(answer_key[0], str)

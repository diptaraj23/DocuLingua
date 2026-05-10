from app.learning.content_schema import DocumentOverview, VocabularyItem
from app.learning.groq_guide_generator import (
    generate_key_vocabulary_with_groq,
    generate_overview_with_groq,
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

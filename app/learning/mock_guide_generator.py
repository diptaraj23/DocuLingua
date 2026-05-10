"""Deterministic mock learning guide generation for the MVP PDF flow."""

from __future__ import annotations

from typing import Any

from app.learning.content_schema import (
    DocumentOverview,
    GrammarPattern,
    LearningGuide,
    LearningStatistics,
    MiniLesson,
    PracticeExercise,
    ReadingPractice,
    ReviewSheet,
    UsefulPhrase,
    VerbItem,
    VocabularyGroup,
    VocabularyItem,
)


def create_mock_learning_guide(
    clean_text: str,
    stats: dict[str, Any],
    source_language: str = "French",
    explanation_language: str = "English",
    learner_level: str = "A2",
    overview: DocumentOverview | None = None,
    key_vocabulary: list[VocabularyItem] | None = None,
) -> LearningGuide:
    """Create a complete mock guide without calling an LLM provider."""

    topic = "music, emotions, and memories"
    word_count = stats.get("word_count", 0)
    paragraph_count = stats.get("paragraph_count", 0)

    mock_key_vocabulary = [
        VocabularyItem(
            term="la chanson",
            translation="the song",
            part_of_speech="noun",
            example_sentence="La vieille chanson revient dans ses souvenirs.",
            note="Useful for discussing music and repeated memories.",
        ),
        VocabularyItem(
            term="le souvenir",
            translation="the memory",
            part_of_speech="noun",
            example_sentence="Ce souvenir reste lumineux.",
            note="Often used with verbs like garder, revenir, and rappeler.",
        ),
        VocabularyItem(
            term="la pluie",
            translation="the rain",
            part_of_speech="noun",
            example_sentence="La pluie tombe doucement sur les vitres.",
            note="A common setting word for mood and atmosphere.",
        ),
        VocabularyItem(
            term="la voix",
            translation="the voice",
            part_of_speech="noun",
            example_sentence="La voix de son grand-pere revient avec la musique.",
            note="Good for describing people and memory.",
        ),
        VocabularyItem(
            term="apprendre par coeur",
            translation="to learn by heart",
            part_of_speech="expression",
            example_sentence="Elle decide d'apprendre la chanson par coeur.",
            note="A practical phrase for language learning.",
        ),
    ]

    vocabulary_groups = [
        VocabularyGroup(
            topic="Music",
            items=[
                VocabularyItem(term="la melodie", translation="melody"),
                VocabularyItem(term="la note", translation="note"),
                VocabularyItem(term="chanter", translation="to sing"),
            ],
        ),
        VocabularyGroup(
            topic="Emotions and Memory",
            items=[
                VocabularyItem(term="l'emotion", translation="emotion"),
                VocabularyItem(term="lumineux", translation="bright"),
                VocabularyItem(term="rappeler", translation="to remind"),
            ],
        ),
    ]

    important_verbs = [
        VerbItem(
            infinitive="revenir",
            translation="to come back",
            tense_or_form="present / imperfect context",
            example_sentence="La chanson revenait toujours.",
        ),
        VerbItem(
            infinitive="entendre",
            translation="to hear",
            tense_or_form="imperfect",
            example_sentence="Elise l'entendait depuis la cuisine.",
        ),
        VerbItem(
            infinitive="decider",
            translation="to decide",
            tense_or_form="past historic / narrative",
            example_sentence="Elle decida d'apprendre la chanson.",
        ),
    ]

    grammar_patterns = [
        GrammarPattern(
            name="The imperfect for background description",
            explanation="The imperfect often describes repeated actions, settings, and emotional background.",
            examples=["La chanson revenait toujours.", "La pluie tombait doucement."],
        ),
        GrammarPattern(
            name="Infinitive after a decision",
            explanation="French often uses de plus an infinitive after verbs like decider.",
            examples=["Elle decida d'apprendre la chanson.", "Il essaie de chanter."],
        ),
        GrammarPattern(
            name="Adjectives after nouns",
            explanation="Many descriptive adjectives appear after the noun in French.",
            examples=["un amour perdu", "le cafe chaud"],
        ),
    ]

    useful_phrases = [
        UsefulPhrase(
            phrase="Cela me rappelle...",
            translation="That reminds me of...",
            usage_note="Use it to connect a song, smell, or place to a memory.",
        ),
        UsefulPhrase(
            phrase="J'ai appris cette chanson par coeur.",
            translation="I learned this song by heart.",
            usage_note="Useful when talking about songs, poems, or dialogues.",
        ),
        UsefulPhrase(
            phrase="La musique garde les emotions.",
            translation="Music keeps emotions.",
            usage_note="A poetic structure for discussing feelings.",
        ),
    ]

    mini_lessons = [
        MiniLesson(
            title="Talking about memories",
            explanation="Use rappeler, souvenir, and revenir to describe how memories return.",
            examples=["Cette melodie me rappelle mon village.", "Un souvenir revient."],
            practice_tip="Write two sentences about a song that reminds you of a place.",
        ),
        MiniLesson(
            title="Setting a scene with the imperfect",
            explanation="The imperfect creates the background of a story before a key action happens.",
            examples=["La pluie tombait.", "Elle ecoutait la chanson."],
            practice_tip="Describe the weather and sound in one short scene.",
        ),
    ]

    practice_exercises = [
        PracticeExercise(
            title="Vocabulary Match",
            instructions="Match each French word with its English meaning.",
            questions=[
                "1. la chanson | a. memory",
                "2. le souvenir | b. song",
                "3. la pluie | c. rain",
            ],
            answers=["1-b", "2-a", "3-c"],
        ),
        PracticeExercise(
            title="Complete the Sentences",
            instructions="Choose a word from the guide to complete each sentence.",
            questions=[
                "La vieille ____ revient le dimanche.",
                "Cette melodie me ____ mon grand-pere.",
                "Elle decide d'apprendre la chanson par ____.",
            ],
            answers=["chanson", "rappelle", "coeur"],
        ),
    ]

    reading_practice = ReadingPractice(
        passage=(
            "Le dimanche matin, Elise ecoute une vieille chanson. La melodie lui rappelle "
            "son grand-pere, la pluie sur les vitres, et les souvenirs de son village."
        ),
        questions=[
            "Quand Elise ecoute-t-elle la chanson?",
            "Qui la melodie lui rappelle-t-elle?",
            "Quels souvenirs reviennent?",
        ],
        answers=["Le dimanche matin.", "Son grand-pere.", "La pluie, le village, et des souvenirs d'ete."],
    )

    review_sheet = ReviewSheet(
        key_points=[
            "Use the imperfect to describe repeated memories and background scenes.",
            "Practice music and memory vocabulary together.",
            "Use short phrases to connect emotions to real experiences.",
        ],
        vocabulary_to_review=["la chanson", "le souvenir", "la melodie", "rappeler", "apprendre par coeur"],
        grammar_to_review=["imperfect tense", "de + infinitive", "adjective placement"],
        study_plan=[
            "Read the vocabulary aloud.",
            "Review the grammar examples.",
            "Complete the exercises, then check the answer key.",
        ],
    )

    learning_statistics = LearningStatistics(
        vocabulary_count=len(key_vocabulary or mock_key_vocabulary),
        topic_specific_words=sum(len(group.items) for group in vocabulary_groups),
        important_verbs=len(important_verbs),
        useful_phrases=len(useful_phrases),
        grammar_concepts=len(grammar_patterns),
        practice_exercises=len(practice_exercises),
        mini_lessons=len(mini_lessons),
    )

    mock_overview = DocumentOverview(
        summary=(
            f"This sample guide treats the uploaded document as a short French text about {topic}. "
            f"The processed text contains about {word_count} words across {paragraph_count} paragraphs."
        ),
        estimated_level=learner_level,
        difficulty_notes="Best suited for learners practicing familiar narrative vocabulary and the imperfect tense.",
        learning_statistics=learning_statistics,
        main_learning_focus=[
            "Music and memory vocabulary",
            "Emotion-focused expressions",
            "Imperfect tense for atmosphere and repeated action",
        ],
        suggested_study_approach=[
            "Preview the vocabulary before rereading the source document.",
            "Study the grammar patterns with the example sentences.",
            "Complete the practice exercises and check the answer key.",
        ],
    )
    selected_overview = overview or mock_overview
    selected_overview.learning_statistics = learning_statistics

    return LearningGuide(
        title="DocuLingua Sample French Learning Guide",
        source_language=source_language,
        explanation_language=explanation_language,
        learner_level=learner_level,
        topic=topic,
        overview=selected_overview,
        key_vocabulary=key_vocabulary or mock_key_vocabulary,
        vocabulary_groups=vocabulary_groups,
        important_verbs=important_verbs,
        grammar_patterns=grammar_patterns,
        useful_phrases=useful_phrases,
        mini_lessons=mini_lessons,
        practice_exercises=practice_exercises,
        reading_practice=reading_practice,
        review_sheet=review_sheet,
        answer_key=[
            "Vocabulary Match: 1-b, 2-a, 3-c.",
            "Complete the Sentences: chanson, rappelle, coeur.",
            "Reading Practice: see the reading answers listed in the section.",
        ],
    )

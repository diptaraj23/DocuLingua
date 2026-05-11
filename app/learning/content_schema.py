"""Pydantic models for the DocuLingua learning guide."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.llm.providers.metadata import GuideGenerationMetadata


class LearningStatistics(BaseModel):
    """Counts shown in the guide overview."""

    vocabulary_count: int = 0
    topic_specific_words: int = 0
    important_verbs: int = 0
    useful_phrases: int = 0
    grammar_concepts: int = 0
    practice_exercises: int = 0
    mini_lessons: int = 0


class DocumentOverview(BaseModel):
    """High-level context for the uploaded document."""

    summary: str = ""
    estimated_level: str = "A2"
    difficulty_notes: str = ""
    learning_statistics: LearningStatistics = Field(default_factory=LearningStatistics)
    main_learning_focus: list[str] = Field(default_factory=list)
    suggested_study_approach: list[str] = Field(default_factory=list)


class VocabularyItem(BaseModel):
    """A key vocabulary item with an explanation."""

    term: str
    translation: str = ""
    part_of_speech: str = ""
    example_sentence: str = ""
    note: str = ""


class VocabularyGroup(BaseModel):
    """Topic-based vocabulary group."""

    topic: str
    items: list[VocabularyItem] = Field(default_factory=list)


class VerbItem(BaseModel):
    """Important verb from the source document."""

    infinitive: str
    translation: str = ""
    example_sentence: str = ""
    tense_or_form: str = ""


class GrammarPattern(BaseModel):
    """Grammar concept connected to the source document."""

    name: str
    explanation: str = ""
    examples: list[str] = Field(default_factory=list)


class UsefulPhrase(BaseModel):
    """Reusable phrase or expression."""

    phrase: str
    translation: str = ""
    usage_note: str = ""


class MiniLesson(BaseModel):
    """Short language lesson for the PDF workbook."""

    title: str
    explanation: str = ""
    examples: list[str] = Field(default_factory=list)
    practice_tip: str = ""


class PracticeExercise(BaseModel):
    """Static practice exercise for the learner."""

    title: str
    instructions: str = ""
    questions: list[str] = Field(default_factory=list)
    answers: list[str] = Field(default_factory=list)


class ReadingPractice(BaseModel):
    """Short reading passage and comprehension questions."""

    passage: str = ""
    questions: list[str] = Field(default_factory=list)
    answers: list[str] = Field(default_factory=list)


class ReviewSheet(BaseModel):
    """Concise review sheet for the end of the guide."""

    key_points: list[str] = Field(default_factory=list)
    vocabulary_to_review: list[str] = Field(default_factory=list)
    grammar_to_review: list[str] = Field(default_factory=list)
    study_plan: list[str] = Field(default_factory=list)


class LearningGuide(BaseModel):
    """Complete static PDF learning guide structure."""

    title: str
    source_language: str = "French"
    explanation_language: str = "English"
    learner_level: str = "A2"
    topic: str = ""
    overview: DocumentOverview = Field(default_factory=DocumentOverview)
    key_vocabulary: list[VocabularyItem] = Field(default_factory=list)
    vocabulary_groups: list[VocabularyGroup] = Field(default_factory=list)
    important_verbs: list[VerbItem] = Field(default_factory=list)
    grammar_patterns: list[GrammarPattern] = Field(default_factory=list)
    useful_phrases: list[UsefulPhrase] = Field(default_factory=list)
    mini_lessons: list[MiniLesson] = Field(default_factory=list)
    practice_exercises: list[PracticeExercise] = Field(default_factory=list)
    reading_practice: ReadingPractice = Field(default_factory=ReadingPractice)
    review_sheet: ReviewSheet = Field(default_factory=ReviewSheet)
    answer_key: list[str] = Field(default_factory=list)
    generation_metadata: GuideGenerationMetadata | None = None

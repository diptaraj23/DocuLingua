"""Prompt builders for DocuLingua Groq content generation."""

from __future__ import annotations


MAX_PROMPT_TEXT_CHARS = 8000


def _truncate_text(clean_text: str, max_chars: int = MAX_PROMPT_TEXT_CHARS) -> str:
    """Limit prompt input size for MVP-friendly Groq usage."""

    return clean_text[:max_chars].strip()


def build_document_overview_prompt(
    clean_text: str,
    stats: dict,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for the document overview section."""

    text = _truncate_text(clean_text)
    return f"""
You are creating a concise language-learning guide for a learner.

Task:
Analyze this {source_language} document as language-learning context.
Do not translate sentence by sentence.
Do not create a direct translation section.
Do not copy tables or long passages from the source document.
Explain what the learner can study from the document: topic, useful vocabulary, likely grammar patterns, and study approach.
Keep all text concise and PDF-friendly.

Learner level: {learner_level}
Explanation language: {explanation_language}
Document statistics: {stats}

Document text is inside these tags:
<document>
{text}
</document>

return JSON only. Your entire response must start with {{ and end with }}.
Use this exact JSON structure:
{{
  "summary": "...",
  "estimated_level": "...",
  "difficulty_notes": "...",
  "main_learning_focus": ["...", "..."],
  "suggested_study_approach": ["...", "..."]
}}

""".strip()


def build_key_vocabulary_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_words: int = 30,
) -> str:
    """Build a JSON-only prompt for the key vocabulary section."""

    text = _truncate_text(clean_text)
    return f"""
You are a vocabulary extraction API for a {learner_level} language learner.

Task:
Choose up to {max_words} useful {source_language} vocabulary items from the document.
Return at least 8 items when the document has enough vocabulary.
Do not translate sentence by sentence.
Select useful learning vocabulary, not every word.
Include frequent, topic-specific, and reusable words.
Avoid proper nouns unless they are educationally important.
Keep explanations concise in {explanation_language}.
Do not copy tables or long passages from the source document.
Do not use source table headers such as "Concept" or "Definition" as JSON keys.
Do not return a dictionary that maps words to meanings.

return JSON only. Your entire response must start with {{ and end with }}.
Use this exact JSON structure:
{{
  "key_vocabulary": [
    {{
      "word": "...",
      "meaning": "...",
      "part_of_speech": "...",
      "why_useful": "..."
    }}
  ]
}}
Every item must use exactly these keys: word, meaning, part_of_speech, why_useful.

Good example:
{{
  "key_vocabulary": [
    {{
      "word": "la mélodie",
      "meaning": "melody",
      "part_of_speech": "noun",
      "why_useful": "Useful for discussing music and sound."
    }}
  ]
}}

Document text is inside these tags:
<document>
{text}
</document>
""".strip()


def build_grammar_patterns_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_patterns: int = 5,
) -> str:
    """Build a JSON-only prompt for grammar patterns."""

    text = _truncate_text(clean_text)
    return f"""
You are identifying grammar patterns for a {learner_level} learner.

Task:
Identify up to {max_patterns} useful grammar patterns that appear in or are strongly suggested by this {source_language} document.
Return JSON only.
Keep explanations beginner-friendly in {explanation_language}.
Avoid advanced grammar unless it is clearly needed.
Use examples in {source_language}, but explain them in {explanation_language}.
Do not translate sentence by sentence.
Focus on reusable grammar patterns.
Keep output concise and PDF-friendly.
Do not return a dictionary that maps grammar names to explanations.
Do not use source table headers as JSON keys.

Document text is inside these tags:
<document>
{text}
</document>

return JSON only. Your entire response must start with {{ and end with }}.
Use this exact JSON structure:
{{
  "grammar_patterns": [
    {{
      "title": "...",
      "explanation": "...",
      "examples": ["...", "..."],
      "learning_note": "..."
    }}
  ]
}}
Every item must use exactly these keys: title, explanation, examples, learning_note.

Good example:
{{
  "grammar_patterns": [
    {{
      "title": "Using the present tense for definitions",
      "explanation": "French often uses the present tense to explain what something is or does.",
      "examples": ["Le rythme organise la musique."],
      "learning_note": "Useful for explaining concepts clearly."
    }}
  ]
}}
""".strip()


def build_useful_phrases_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_phrases: int = 15,
) -> str:
    """Build a JSON-only prompt for useful phrases and expressions."""

    text = _truncate_text(clean_text)
    return f"""
You are extracting reusable phrases for a {learner_level} learner.

Task:
Extract up to {max_phrases} useful phrases and expressions from or inspired by this {source_language} document.
Return JSON only.
Prefer phrases useful beyond this one document.
Avoid full sentence-by-sentence translation.
Include expressions useful for speaking or writing about the document topic.
Keep meanings concise in {explanation_language}.

Document text is inside these tags:
<document>
{text}
</document>

return JSON only. Your entire response must start with {{ and end with }}.
Use this exact JSON structure:
{{
  "useful_phrases": [
    {{
      "phrase": "...",
      "meaning": "...",
      "usage_note": "..."
    }}
  ]
}}
Every item must use exactly these keys: phrase, meaning, usage_note.
""".strip()


def build_mini_lessons_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_lessons: int = 4,
) -> str:
    """Build a JSON-only prompt for mini language lessons."""

    text = _truncate_text(clean_text)
    return f"""
You are creating short language lessons for a {learner_level} learner.

Task:
Create up to {max_lessons} short mini lessons inspired by this {source_language} document.
Return JSON only.
The lessons should help the learner use the language, not just understand this one document.
Each lesson should have a clear objective.
Examples should be simple and useful.
Do not create exercises here.
Do not create sentence-wise translation.
Keep content concise and suitable for a generated PDF workbook.
Write explanations in {explanation_language}.

Document text is inside these tags:
<document>
{text}
</document>

return JSON only. Your entire response must start with {{ and end with }}.
Use this exact JSON structure:
{{
  "mini_lessons": [
    {{
      "title": "...",
      "objective": "...",
      "explanation": "...",
      "examples": ["...", "..."]
    }}
  ]
}}
Every item must use exactly these keys: title, objective, explanation, examples.
""".strip()


def build_important_verbs_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_verbs: int = 15,
) -> str:
    """Build a JSON-only prompt for important verbs."""

    text = _truncate_text(clean_text)
    return f"""
Extract up to {max_verbs} useful verbs from this {source_language} document for a {learner_level} learner.
Return JSON only.
Prefer common and reusable verbs that help the learner discuss the document topic.
Keep explanations beginner-friendly in {explanation_language}.
Do not translate the document sentence by sentence.

Expected JSON:
{{
  "important_verbs": [
    {{"verb": "...", "meaning": "...", "common_form": "...", "learning_note": "..."}}
  ]
}}

Document:
<document>
{text}
</document>
""".strip()


def build_practice_exercises_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
    max_exercises: int = 10,
) -> str:
    """Build a JSON-only prompt for static practice exercises."""

    text = _truncate_text(clean_text)
    return f"""
Create up to {max_exercises} static PDF-friendly language exercises for a {learner_level} learner.
Return JSON only.
Use types such as vocabulary matching, fill in the blanks, article choice, verb choice, and short writing prompts.
Include the answer for every exercise.
Do not create interactive exercises.
Do not create sentence-wise translation.

Expected JSON:
{{
  "practice_exercises": [
    {{"instruction": "...", "question": "...", "answer": "..."}}
  ]
}}

Document:
<document>
{text}
</document>
""".strip()


def build_reading_practice_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for reading practice."""

    text = _truncate_text(clean_text)
    return f"""
Create a short simplified reading passage in {source_language} for a {learner_level} learner.
Return JSON only.
The passage should be inspired by the document context, not copied from the document.
Include vocabulary help, comprehension questions, and answers.
Do not translate the whole passage sentence by sentence.

Expected JSON:
{{
  "reading_practice": {{
    "title": "...",
    "passage": "...",
    "vocabulary_help": ["...", "..."],
    "questions": ["...", "..."],
    "answers": ["...", "..."]
  }}
}}

Document:
<document>
{text}
</document>
""".strip()


def build_review_sheet_prompt(
    clean_text: str,
    source_language: str,
    explanation_language: str,
    learner_level: str,
) -> str:
    """Build a JSON-only prompt for the review sheet."""

    text = _truncate_text(clean_text)
    return f"""
Create a concise one-page-style review sheet for a {learner_level} learner.
Return JSON only.
Include the most useful things the learner should remember.
Keep it PDF-friendly.
Avoid sentence-wise translation.

Expected JSON:
{{
  "review_sheet": {{
    "top_vocabulary": ["...", "..."],
    "top_verbs": ["...", "..."],
    "top_phrases": ["...", "..."],
    "grammar_points": ["...", "..."],
    "study_tips": ["...", "..."]
  }}
}}

Document:
<document>
{text}
</document>
""".strip()


def build_answer_key_prompt(
    exercises: list,
    reading_practice: dict,
    source_language: str,
    explanation_language: str,
) -> str:
    """Build a JSON-only prompt for the answer key."""

    return f"""
Create a concise answer key in {explanation_language} for these static exercises and reading practice.
Return JSON only.
Number answers clearly.
Do not add unnecessary explanations unless helpful.

Expected JSON:
{{
  "answer_key": ["...", "..."]
}}

Exercises:
{exercises}

Reading practice:
{reading_practice}

Source language: {source_language}
""".strip()

GRAMMAR_PROMPT = """
Identify useful grammar patterns in the document for the learner's level.
"""

MINI_LESSON_PROMPT = """
Create short mini lessons connected to the document topic and vocabulary.
"""

EXERCISE_PROMPT = """
Create static practice exercises suitable for a printable learning guide.
"""

REVIEW_SHEET_PROMPT = """
Create a concise review sheet and answer key for the generated learning guide.
"""

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
You are selecting key vocabulary for a {learner_level} learner.

Task:
Choose up to {max_words} useful {source_language} vocabulary items from the document.
Return at least 8 items when the document has enough vocabulary.
Do not translate sentence by sentence.
Select useful learning vocabulary, not every word.
Include frequent, topic-specific, and reusable words.
Avoid proper nouns unless they are educationally important.
Keep explanations concise in {explanation_language}.
Do not copy tables or long passages from the source document.

Document text is inside these tags:
<document>
{text}
</document>

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

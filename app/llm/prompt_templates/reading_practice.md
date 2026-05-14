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

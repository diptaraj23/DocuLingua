Create up to {max_exercises} static PDF-friendly language exercises for a {learner_level} learner.
Return JSON only.
Use types such as vocabulary matching, fill in the blanks, article choice, verb choice, and short writing prompts.
Include the answer for every exercise.
Each item must be one clear printable prompt, not a whole worksheet.
Do not number inside the "question" field; the PDF will add numbering.
Keep matching exercises short, for example one prompt with 3-5 pairs, not a dense paragraph.
Use {source_language} inside questions when the learner is practicing the language.
Keep answers concise and directly checkable.
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

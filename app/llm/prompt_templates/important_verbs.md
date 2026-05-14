Extract up to {max_verbs} useful verbs from this {source_language} document for a {learner_level} learner.
Return JSON only.
Prefer common and reusable verbs that help the learner discuss the document topic.
Keep explanations beginner-friendly in {explanation_language}.
Use {source_language} for verb forms and examples.
The "common_form" field should be a useful {source_language} form from the document context when possible.
The "learning_note" field should include either a short {source_language} example phrase plus a brief {explanation_language} note, or a concise usage note.
Do not put only an English sentence in "learning_note".
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

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

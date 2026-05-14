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

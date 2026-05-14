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

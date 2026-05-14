Create a concise answer key in {explanation_language} for these static exercises and reading practice.
Return JSON only.
Number answers clearly.
Include each exercise answer once.
Include reading-practice answers only if they are not already included in the exercise answers.
Do not repeat the same reading answer in multiple formats.
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

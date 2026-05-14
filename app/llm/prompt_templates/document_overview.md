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

Create a concise one-page-style review sheet for a {learner_level} learner.
Return JSON only.
Include the most useful things the learner should remember.
Keep it PDF-friendly.
Make it feel like a revision page, not a raw word dump.
Limit each list to the strongest items.
Use short labels such as "Vocabulary to remember", "Grammar to review", and "Study actions" in the wording where useful.
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

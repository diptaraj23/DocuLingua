# Annex C: Demo

## Demo Video / GIF Link

`[Add demo video or GIF link here]`

## Suggested Demo Script

1. Open DocuLingua with `streamlit run streamlit_app.py`.
2. Show the source language, explanation language, and learner level controls.
3. Upload a French PDF or TXT document, or select a stored upload.
4. Click **Process Document**.
5. Show document metrics, cleaned text preview, and first chunk preview.
6. Open the API settings popover and show where Groq and Gemini keys are configured, without revealing real keys.
7. Click **Generate PDF Guide**.
8. Show progress rows, provider/model metadata, vocabulary count, grammar count, exercise count, and output filename.
9. Download the generated PDF.
10. Open the PDF and briefly show the overview, vocabulary, grammar, exercises, review sheet, and answer key.
11. Briefly show the GitHub repository structure, including `streamlit_app.py`, `app/core/`, `app/llm/`, `app/learning/`, `app/pdf/`, and `tests/`.

## What the Professor Should See

- A document can be uploaded or selected from local storage.
- DocuLingua extracts and previews document text before generation.
- LLM-generated sections are organized into a structured learning guide.
- The final output is a downloadable static PDF workbook.
- The repository has modular source code and automated tests.

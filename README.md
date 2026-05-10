# DocuLingua

DocuLingua is a Streamlit and Python MVP that turns a foreign-language document, initially French, into a static PDF learning guide. Instead of producing sentence-by-sentence translation, it helps learners study French through the vocabulary, grammar, topics, and expressions found in the uploaded document.

## Problem Statement

Learners often bring real-world documents to language study, but raw documents can be difficult to approach without support. DocuLingua aims to transform an uploaded text into a structured workbook that explains what to focus on, which words matter, and how to practice the language in context.

## MVP Scope

The first MVP is intentionally simple:

- Upload a PDF or TXT document in Streamlit.
- Extract and clean document text locally.
- Generate language-learning content with the Groq API in a future phase.
- Render a static downloadable PDF workbook with Jinja2 and WeasyPrint.
- Store uploads, generated files, and cache files locally.

The MVP does not include a database, user accounts, FastAPI, Docker, interactive exercises, or sentence-wise translation.

## Generated PDF Contents

The planned PDF workbook contains:

1. Cover Page
2. Document Context Overview
3. Key Vocabulary
4. Topic-Based Vocabulary Groups
5. Important Verbs
6. Grammar Patterns
7. Useful Phrases and Expressions
8. Mini Language Lessons
9. Practice Exercises
10. Short Reading Practice
11. Review Sheet
12. Answer Key

## Tech Stack

- Frontend: Streamlit
- Backend: Python
- LLM provider: Groq API
- PDF generation: Jinja2 and WeasyPrint
- PDF extraction: PyMuPDF
- TXT extraction: Python standard library
- Configuration: python-dotenv and pydantic-settings
- Schema validation: Pydantic
- Planned NLP support: spaCy
- Testing: pytest

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and add your Groq API key when you are ready to implement generation:

```text
GROQ_API_KEY=
GROQ_MAIN_MODEL=llama-3.3-70b-versatile
GROQ_FAST_MODEL=llama-3.1-8b-instant
```

The current starter app does not require a working Groq API key.

## Run Streamlit

```powershell
streamlit run streamlit_app.py
```

## Roadmap

- Phase 1: Repository skeleton and starter documentation
- Phase 2: Robust PDF/TXT text extraction
- Phase 3: Learning guide schema and content validation
- Phase 4: Groq prompt design and response parsing
- Phase 5: PDF rendering with polished workbook templates
- Phase 6: Streamlit integration and download flow
- Phase 7: Testing, error handling, and UX polish

## Current Status

Phase 1, Phase 2 document ingestion, the first non-LLM PDF flow, and the first Groq-powered content step are implemented. The app supports document upload, TXT/PDF extraction, text cleaning, deterministic chunking, document statistics, mock `LearningGuide` generation, static PDF rendering, and Streamlit PDF download.

The Groq client wrapper and prompt builders now cover the full generated learning guide: overview, vocabulary, verbs, grammar, phrases, mini lessons, exercises, reading practice, review sheet, and answer key. The output remains a static PDF. DocuLingua does not generate sentence-wise translation or interactive exercises.

Tests use mocked Groq responses and do not call the real API.

To use Groq:

1. Copy `.env.example` to `.env`.
2. Add `GROQ_API_KEY`.
3. Run Streamlit.
4. Enable the Groq checkbox in the UI.

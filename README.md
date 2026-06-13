# DocuLingua

DocuLingua is a Streamlit and Python MVP that turns a foreign-language document, initially French, into a static PDF learning guide. Instead of producing sentence-by-sentence translation, it helps learners study French through the vocabulary, grammar, topics, and expressions found in the uploaded document.

## Problem Statement

Learners often bring real-world documents to language study, but raw documents can be difficult to approach without support. DocuLingua aims to transform an uploaded text into a structured workbook that explains what to focus on, which words matter, and how to practice the language in context.

## MVP Scope

The first MVP is intentionally simple:

- Upload a PDF or TXT document in Streamlit.
- Extract and clean document text locally.
- Generate language-learning content with modular LLM providers.
- Render a static downloadable PDF workbook with WeasyPrint/PyMuPDF(as a fall back option).
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
- LLM providers: Groq first, Gemini fallback
- PDF generation: WeasyPrint/PyMuPDF
- PDF extraction: WeasyPrint/PyMuPDF
- TXT extraction: Python standard library
- Configuration: python-dotenv and pydantic-settings
- Schema validation: Pydantic
- Planned NLP support: spaCy
- Testing: pytest

## Setup
Before creating an virtual environment, you need to install WeasyPrint dependencies. To do so visit their website and follow the easy [installation guid](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation).

However, you can skip installing WeasyPrint dependencies and the application still works, the only catch is that it uses PyMuPDF to generate the PDFs. Therefore, the generated material might not be as tidy and clean as WeasyPrint, but it's still acceptable.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```
## Environment Variables (New Version)
Just run the application, on the main screen, click on setting icon "⚙️", then specify your api keys for Groq and Gemini in the designated fields. You can save your API-key configuration (equivalent to manually write to .env), and even more, you can test your API keys live in the setting pane.

## Environment Variables (Old Version)

Copy `.env.example` to `.env` and add provider API keys:

```text
GROQ_API_KEY=
GROQ_MAIN_MODEL=llama-3.3-70b-versatile
GROQ_FAST_MODEL=llama-3.1-8b-instant

GEMINI_API_KEY=
GEMINI_MAIN_MODEL=gemini-2.5-flash
GEMINI_FAST_MODEL=gemini-2.5-flash-lite

PRIMARY_LLM_PROVIDER=groq
FALLBACK_LLM_PROVIDERS=gemini
```

LLM generation is optional in the UI. If LLM generation is disabled, the app can still create a mock/sample guide.

NOTE: It is highly recommended to use paid api keys instead of free ones for better user experience. However, you can generate and use your free api keys as well, to do so, we refer you to these tutorials: [Groq](https://www.youtube.com/watch?v=6BRyynZkvf0) and [Gemini](https://www.youtube.com/watch?v=9VDbhptCzlU).

## Multi-Provider LLM Design

DocuLingua uses a provider router for structured JSON generation. The default order is:

1. Groq
2. Gemini fallback

If Groq is rate-limited, unavailable, returns invalid JSON, or returns JSON that cannot be validated into the expected section schema, the router tries Gemini. Every provider response goes through the same JSON parser and Pydantic validation path before content is accepted.

Future providers such as OpenRouter, GitHub Models, or NVIDIA NIM can be added by implementing `BaseLLMProvider` and registering the provider in the router.

## Run Streamlit

```powershell
streamlit run streamlit_app.py
```

## Roadmap

- Phase 1: Repository skeleton and starter documentation
- Phase 2: Robust PDF/TXT text extraction
- Phase 3: Learning guide schema and content validation
- Phase 4: LLM prompt design, provider routing, and response parsing
- Phase 5: PDF rendering with polished workbook templates
- Phase 6: Streamlit integration and download flow
- Phase 7: Testing, error handling, and UX polish

## Current Status

Phase 1, Phase 2 document ingestion, the first non-LLM PDF flow, and full LLM-powered content generation are implemented. The app supports document upload, TXT/PDF extraction, text cleaning, deterministic chunking, document statistics, mock `LearningGuide` generation, static PDF rendering, and Streamlit PDF download.

The LLM provider layer now covers the full generated learning guide: overview, vocabulary, verbs, grammar, phrases, mini lessons, exercises, reading practice, review sheet, and answer key. The output remains a static PDF. DocuLingua does not generate sentence-wise translation or interactive exercises.

The provider router records which provider and model generated each section. Generation metadata appears in Streamlit and in the generated PDF. The pipeline includes safer JSON parsing, JSON extraction from messy responses, retry on invalid JSON, section-level mock fallback, Streamlit warnings for failed sections, and basic logging for debugging.

The Streamlit generation flow also shows real-time progress: an overall progress bar, checklist-style process table, status icons, per-step duration, and provider/model labels for LLM-generated sections.

An optional final Learning Material Polisher can run after the guide is generated. It now polishes each content section separately, validates each polished section back into the existing schema, improves flow and workbook tone, and can fall back to the unpolished section if a polishing call fails. This improves PDF readability but may use several additional provider calls.

Prompt text is stored in Markdown templates under `app/llm/prompt_templates/`. The Python prompt builder functions in `app/llm/prompts.py` load and render those templates so prompts can be edited without digging through large Python strings.

Tests use mocked provider responses and do not call real APIs.

To use LLM generation:

1. Copy `.env.example` to `.env`.
2. Add `GROQ_API_KEY` and optionally `GEMINI_API_KEY`.
3. Run Streamlit.
4. Enable the LLM checkbox in the UI.

# Annex D: Technical Notes

## Setup Instructions

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run streamlit_app.py
```

## Environment Variables

The `.env.example` file documents the expected configuration:

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

The current `app/config.py` also defines default model values for Groq and Gemini. Verify the final model names before submission if the project will be demonstrated live.

## Known Limitations

- The MVP focuses on static PDF learning guides, not interactive exercises.
- The README states that sentence-wise translation is not part of the application scope.
- LLM generation requires a valid Groq or Gemini API key.
- WeasyPrint may require native system libraries on Windows. If those are unavailable, the application falls back to PyMuPDF for PDF generation.
- The current pipeline truncates LLM input to a maximum configured character length for the MVP.
- No database is implemented; storage is local file based.
- No deployment link or demo video was found in the repository.

## Future Improvements

- Add a demo video or GIF link.
- Add screenshots of the Streamlit workflow and generated PDF.
- Add deployment instructions if a hosted version is created.
- Improve large-document handling by processing multiple chunks through the LLM layer.
- Add more provider adapters if required by future project scope.

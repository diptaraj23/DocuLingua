# Project Report: DocuLingua

**GROUPE MEMEBERS**: **Amirarsalan Sanati**, **Diptaraj Sen**

## 1. Project Idea

DocuLingua is a Python and Streamlit application that helps language learners study a foreign-language document by turning uploaded PDF or TXT content into a structured learning guide. The current repository focuses on French source documents with English explanations, and the intended users are learners who want vocabulary, grammar, phrases, exercises, and review material from real texts rather than generic textbook examples.

The application extracts and cleans document text locally, prepares document statistics and chunks, generates learning sections through configurable LLM providers, and exports a static PDF workbook. The repository uses Streamlit for the user interface, PyMuPDF for PDF text extraction and fallback PDF generation, optional WeasyPrint rendering, Pydantic models for guide structure, Groq and Gemini provider adapters for LLM output, python-dotenv and pydantic-settings for configuration, and pytest for automated tests.

## 2. Achieved Tasks and Features

- Supports document input through Streamlit file upload and previously stored uploads.
- Accepts `.pdf` and `.txt` files and rejects unsupported file extensions.
- Extracts PDF text with PyMuPDF and reads TXT files as UTF-8 text.
- Cleans text, chunks content, and calculates document statistics such as characters, words, paragraphs, unique words, and estimated reading time.
- Provides a Streamlit preview workflow with metrics, cleaned text preview, and first chunk preview.
- Generates learning-guide sections for overview, key vocabulary, important verbs, grammar patterns, useful phrases, mini lessons, practice exercises, reading practice, review sheet, and answer key.
- Uses a provider router that tries configured LLM providers in order, with Groq as the primary provider and Gemini as fallback by default.
- Parses JSON responses, validates section data with Pydantic-backed structures, records provider/model metadata, and reports failed sections.
- Includes optional final guide polishing through additional LLM calls.
- Renders a downloadable static PDF guide using WeasyPrint when available and PyMuPDF as a fallback.
- Stores uploads and generated PDFs locally under `app/storage/`.
- Provides API key settings in the Streamlit interface and supports `.env` configuration.
- Includes automated pytest coverage for document loading, text cleaning, chunking, provider routing, response parsing, guide generation, PDF building, progress tracking, and schemas.

## 3. Software Development Principles Followed

- **Modularity:** The project separates UI, core processing, learning content generation, LLM providers, PDF rendering, and utilities into distinct modules.
- **Separation of concerns:** `streamlit_app.py` handles interaction, `app/core/` handles document processing, `app/learning/` handles guide content, `app/llm/` handles prompts and providers, and `app/pdf/` handles PDF output.
- **Design modeling:** Created design models (usecase, sequence, architecture etc.) following design modeling principles.
- **Complying with principels guiding process**: Create somethign which brings value for the user.
- **Single responsibility:** Individual helpers such as document loaders, text cleaners, response parsers, provider adapters, and PDF builders each focus on one main responsibility.
- **Configuration management:** API keys, model names, provider order, and project settings are loaded through `.env` and `pydantic-settings`.
- **Input validation:** Supported file types are checked, TXT decoding errors are handled, and LLM output is validated before being accepted into the guide.
- **Error handling and fallback:** The provider router records failed attempts, retries invalid JSON, falls back from Groq to Gemini, and the PDF builder falls back from WeasyPrint to PyMuPDF.
- **Extensibility:** New LLM providers can be added by implementing the provider interface and registering them with the router.
- **Testing:** The `tests/` directory contains focused pytest cases that cover local processing and mocked provider behavior without requiring real API calls.
- **Continuous Integration:** CI practices were involved during the development of the software: Regular and granular commits (pushs), unit testing, fall back, github workflows, github actions etc.
- **Documentation:** The README explains the project goal, setup, environment variables, run command, provider design, and current MVP status.

## 4. Demo and Repository Information

- Repository link: https://github.com/diptaraj23/DocuLingua
- Run command:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run streamlit_app.py
```

- Required dependencies are listed in `requirements.txt`: Streamlit, Groq, Google GenAI, python-dotenv, Pydantic, pydantic-settings, PyMuPDF, spaCy, pytest, and WeasyPrint.
- Required environment variables for LLM generation include `GROQ_API_KEY` and optionally `GEMINI_API_KEY`. Model and provider settings are also configurable in `.env`.
- LLM generation requires at least one configured API key. The PDF renderer can use PyMuPDF if WeasyPrint native dependencies are unavailable.

## 5. Annexes 
In this part, we introduce and explain different diagrams illustrating the design of the system.


### Annex A: UML and architecture diagrams.

#### Use Case Diagram

```mermaid
flowchart LR
    User["Language Learner / Student"]
    Developer["Developer / Maintainer"]

    UC1(("Open Streamlit app"))
    UC2(("Upload PDF or TXT document"))
    UC3(("Use stored upload"))
    UC4(("Preview extracted and cleaned text"))
    UC5(("Configure API keys"))
    UC6(("Generate learning material"))
    UC7(("Review vocabulary output"))
    UC8(("Review grammar and practice output"))
    UC9(("Download static PDF guide"))
    UC10(("Run tests and maintain providers"))

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    UC6 --> UC7
    UC6 --> UC8
    User --> UC9

    Developer --> UC10
    Developer --> UC5
```

This diagram shows the main learner actions: opening the Streamlit app, uploading or selecting a document, previewing extracted text, configuring API keys, generating learning material, and downloading the final PDF. It also includes developer maintenance actions such as running tests and managing providers.

#### Class / Module Diagram

```mermaid
flowchart TB
    UI["streamlit_app.py<br/>Streamlit interface, upload controls, API key settings, PDF download"]
    Pipeline["app/core/pipeline.py<br/>Preview processing, guide generation workflow, progress tracking"]
    Loader["app/core/document_loader.py<br/>TXT/PDF loading and uploaded file saving"]
    Text["app/core/text_cleaner.py<br/>app/core/text_chunker.py<br/>app/core/text_stats.py<br/>Cleaning, chunking, document metrics"]
    Schema["app/learning/content_schema.py<br/>Pydantic LearningGuide, vocabulary, grammar, exercises, review sheet"]
    LLMGuide["app/learning/llm_guide_generator.py<br/>Section generation and schema validation"]
    Polisher["app/learning/guide_polisher.py<br/>Optional final editing pass"]
    Mock["app/learning/mock_guide_generator.py<br/>Local sample guide fallback content"]
    Prompts["app/llm/prompts.py and prompt_templates<br/>Prompt construction from Markdown templates"]
    Router["app/llm/providers/router.py<br/>Provider order, fallback, metadata"]
    Base["app/llm/providers/base.py<br/>Provider interface"]
    Groq["app/llm/providers/groq_provider.py<br/>Groq JSON provider"]
    Gemini["app/llm/providers/gemini_provider.py<br/>Gemini JSON provider"]
    Parser["app/llm/response_parser.py<br/>JSON extraction and parsing"]
    PDF["app/pdf/pdf_builder.py<br/>WeasyPrint rendering with PyMuPDF fallback"]
    Config["app/config.py<br/>Environment and provider settings"]
    Storage["app/storage<br/>uploads, outputs, cache"]

    UI --> Pipeline
    UI --> Loader
    UI --> Config
    UI --> Storage
    Pipeline --> Loader
    Pipeline --> Text
    Pipeline --> LLMGuide
    Pipeline --> Mock
    Pipeline --> Polisher
    Pipeline --> PDF
    LLMGuide --> Schema
    LLMGuide --> Prompts
    LLMGuide --> Router
    Polisher --> Router
    Router --> Base
    Router --> Groq
    Router --> Gemini
    Router --> Config
    Groq --> Parser
    Gemini --> Parser
    PDF --> Schema
    PDF --> Storage
```

This diagram represents the repository as cooperating modules. The Streamlit UI calls the core pipeline, the pipeline uses document loading and text processing helpers, the learning layer builds Pydantic-based guide structures, the provider router manages Groq and Gemini adapters, and the PDF builder writes the final workbook.

#### Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant Loader as Document Loader
    participant Core as Core Pipeline
    participant Router as Provider Router
    participant Groq as Groq API
    participant Gemini as Gemini API
    participant PDF as PDF Builder
    participant Storage as Local Storage

    User->>UI: Open application
    User->>UI: Upload or select PDF/TXT document
    UI->>Loader: Save or load selected file
    Loader->>Storage: Store upload if new
    UI->>Core: Process document for preview
    Core->>Loader: Extract document text
    Core->>Core: Clean text, chunk text, calculate statistics
    Core-->>UI: Return preview data and metrics
    User->>UI: Click Generate PDF Guide
    UI->>Core: Generate LLM learning guide PDF
    Core->>Router: Request validated JSON sections
    Router->>Groq: Try primary provider
    alt Groq succeeds
        Groq-->>Router: Valid JSON section
    else Groq unavailable or invalid
        Router->>Gemini: Try fallback provider
        Gemini-->>Router: Valid JSON section or error
    end
    Router-->>Core: Section content and metadata
    Core->>PDF: Build static PDF from LearningGuide
    PDF->>Storage: Save generated PDF
    Core-->>UI: Return PDF path, metadata, progress rows
    UI-->>User: Show download button
    User->>UI: Download generated PDF
```

This diagram follows the main application workflow from opening DocuLingua through document upload, local extraction, preview generation, LLM section generation, static PDF creation, and final download.

#### Architecture Diagram

```mermaid
flowchart TB
    User["User"]
    UI["Streamlit UI<br/>streamlit_app.py"]
    Config["Configuration<br/>.env, pydantic-settings"]
    Storage["Local Storage<br/>uploads, outputs, cache"]
    Core["Core Processing<br/>document_loader, text_cleaner, text_chunker, text_stats, progress_tracker"]
    Learning["Learning Guide Layer<br/>content_schema, llm_guide_generator, guide_polisher, mock_guide_generator"]
    Prompts["Prompt Templates<br/>app/llm/prompt_templates/*.md"]
    Router["LLM Provider Router<br/>fallback and validation"]
    Groq["External Groq API"]
    Gemini["External Gemini API"]
    PDF["PDF Generation<br/>WeasyPrint with PyMuPDF fallback"]
    Tests["Automated Tests<br/>pytest"]

    User --> UI
    UI --> Config
    UI --> Storage
    UI --> Core
    Core --> Storage
    Core --> Learning
    Learning --> Prompts
    Learning --> Router
    Router --> Config
    Router --> Groq
    Router --> Gemini
    Learning --> PDF
    PDF --> Storage
    Tests -. verify .-> Core
    Tests -. verify .-> Learning
    Tests -. verify .-> Router
    Tests -. verify .-> PDF
```

This diagram summarizes the runtime architecture: Streamlit UI, configuration, local storage, core processing, learning-guide generation, prompt templates, provider routing, external LLM APIs, PDF generation, and pytest coverage.

#### Database / Storage

The inspected repository does not contain a database schema, ORM configuration, migration files, or database service configuration. DocuLingua stores files locally instead:

- Uploaded source documents are stored under `app/storage/uploads/`.
- Generated PDF learning guides are stored under `app/storage/outputs/`.
- Cache-related placeholder storage exists under `app/storage/cache/`.
- Runtime configuration is stored in `.env`.

Because the MVP does not use a database, an ER diagram is not applicable. A local storage view is included in the architecture diagram.

The project does not use a database. Local file storage is used for uploads, generated PDFs, cache placeholders, and environment configuration.

## Annex B: Screenshot placeholders.
In this section, we will showcase some screenshots from the software itself, to better demonstrate the developed product and its capabilities:

### Main page, main functionalities.

![main page](./images/main_page_1.png)

Here, is the user input interface:

![main page input](./images/main_page_input.png)

There's an option for the user to select previously uploaded docs (for regeneration):

![prev upload](./images/main_page_input_prev.png)

And you can also choose to delete your previously uploaded documents:

![prev upload manage](./images/main_page_prev_upload_manage.png)

Here, is the learning guide pdf generation user interface:

![pdf gen interface](./images/pdf_guide_gen_interface.png)

And of course you can see and manage previously generated materials:

![pdf gen manage](./images/prev_gen_files_manage.png)

### API Settings.

User can change their api keys without having to directly edit '.env' file:

![API settings](./images/API_settings.png)

User can save, or test the connectivity and authenticity and responsiveness of the keys:

![API tested](./images/API_tested.png)

### Sample run.

After uploading document, the uploaded material will be processed and user will be given some stats regarding the doc:

![doc stats](./images/doc_process.png)

User can see the learning guide generation progress, its pipeline, and its current stage, along with the time took to complete the task and the model used by software to complete it.

![gen prog](./images/generation_progress.png)

After generation is complete, user can download the generated document. Moreover, generation report will be shown to the user:

![gen report](./images/gen_report.png)
![gen report2](./images/gen_report_2.png)
![gen report3](./images/gen_report_3.png)

### See the generated document.

The followign images will showcase a sample generated pdf guide for the uploaded French document, you can see the table of contents, and some sectiones of it. The pdf and the French document is available in the github repository:

![gen result](./images/gen_output_sample_1.png)
![gen result2](./images/gen_output_sample_2.png)
![gen resul3](./images/gen_output_sample_3.png)
![gen resul4](./images/gen_output_sample_4.png)

## Annex C: Future imporvements.

### Known Limitations

- The MVP focuses on static PDF learning guides, not interactive exercises.
- WeasyPrint may require native system libraries on Windows. If those are unavailable, the application falls back to PyMuPDF for PDF generation.
- The current pipeline truncates LLM input to a maximum configured character length for the MVP.
- No database is implemented; storage is local file based.
- Target language only limited to French.

### Future Improvements

- Solve the limitations above.
- Improve large-document handling by processing multiple chunks through the LLM layer.

## Annex D: Acknowledgement.

We would like to acknowledge usage of generative AI in the process of development of this software. We hope that this product brings value to the users and be regarded as a useful tool for language learners.
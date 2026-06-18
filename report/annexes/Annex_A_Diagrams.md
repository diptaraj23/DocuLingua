# Annex A: UML and Architecture Diagrams

## Use Case Diagram

File: `../diagrams/use_case_diagram.mmd`

This diagram shows the main learner actions: opening the Streamlit app, uploading or selecting a document, previewing extracted text, configuring API keys, generating learning material, and downloading the final PDF. It also includes developer maintenance actions such as running tests and managing providers.

## Class / Module Diagram

File: `../diagrams/class_or_module_diagram.mmd`

This diagram represents the repository as cooperating modules. The Streamlit UI calls the core pipeline, the pipeline uses document loading and text processing helpers, the learning layer builds Pydantic-based guide structures, the provider router manages Groq and Gemini adapters, and the PDF builder writes the final workbook.

## Sequence Diagram

File: `../diagrams/sequence_diagram.mmd`

This diagram follows the main application workflow from opening DocuLingua through document upload, local extraction, preview generation, LLM section generation, static PDF creation, and final download.

## Architecture Diagram

File: `../diagrams/architecture_diagram.mmd`

This diagram summarizes the runtime architecture: Streamlit UI, configuration, local storage, core processing, learning-guide generation, prompt templates, provider routing, external LLM APIs, PDF generation, and pytest coverage.

## Database / Storage

File: `../diagrams/database_or_storage_not_applicable.md`

The project does not use a database. Local file storage is used for uploads, generated PDFs, cache placeholders, and environment configuration.

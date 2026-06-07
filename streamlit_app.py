"""Streamlit entry point for the DocuLingua MVP."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

from app.config import settings
from app.core.document_loader import save_uploaded_file
from app.core.pipeline import generate_llm_learning_guide_pdf, process_document_for_preview
from app.core.text_cleaner import is_text_too_short


st.set_page_config(page_title="DocuLingua", page_icon="DL", layout="centered")


def list_stored_files(directory: Path, allowed_suffixes: set[str] | None = None) -> list[Path]:
    if not directory.exists():
        return []

    files = [path for path in directory.iterdir() if path.is_file()]
    if allowed_suffixes is not None:
        files = [path for path in files if path.suffix.lower() in allowed_suffixes]

    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return files


def build_file_rows(files: list[Path]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for path in files:
        stats = path.stat()
        rows.append(
            {
                "name": path.name,
                "size_kb": round(stats.st_size / 1024),
                "modified": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return rows


def delete_file(path: Path) -> None:
    if path.exists() and path.is_file():
        path.unlink()


def reset_processed_state() -> None:
    st.session_state.saved_path = None
    st.session_state.processed = None


upload_dir = settings.project_root / "app" / "storage" / "uploads"
output_dir = settings.project_root / "app" / "storage" / "outputs"
upload_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

if "saved_path" not in st.session_state:
    st.session_state.saved_path = None
if "processed" not in st.session_state:
    st.session_state.processed = None
if "selected_existing_upload" not in st.session_state:
    st.session_state.selected_existing_upload = None


st.title("DocuLingua")
st.caption("Turn a French document into a static PDF learning guide.")

st.write(
    "Upload a PDF or TXT file to extract, clean, chunk, preview, and generate a static PDF learning guide."
)

source_language = st.selectbox("Source language", ["French"], index=0)
explanation_language = st.selectbox("Explanation language", ["English"], index=0)
learner_level = st.selectbox(
    "Learner level",
    ["Beginner", "Elementary", "Intermediate", "Upper intermediate", "Advanced"],
    index=2,
)

st.divider()
st.subheader("Input document")

input_mode = st.radio(
    "Choose input source",
    ["Upload new file", "Use stored upload"],
    horizontal=True,
)

uploaded_file = None
selected_stored_path: Path | None = None

stored_uploads = list_stored_files(upload_dir, allowed_suffixes={".pdf", ".txt"})

if input_mode == "Upload new file":
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])
    if uploaded_file:
        st.info(f"Ready to process: {uploaded_file.name}")
    else:
        st.info("Upload a PDF or TXT file to start the ingestion preview.")
else:
    if stored_uploads:
        selected_name = st.selectbox(
            "Choose a previously uploaded file",
            options=[path.name for path in stored_uploads],
            index=0,
        )
        selected_stored_path = next(path for path in stored_uploads if path.name == selected_name)
        st.info(f"Ready to process stored file: {selected_stored_path.name}")
    else:
        st.info("No stored uploads were found. Upload a new file first.")

st.write(
    f"Source: {source_language} | Explanations: {explanation_language} | "
    f"Level: {learner_level}"
)

process_disabled = False
if input_mode == "Upload new file" and uploaded_file is None:
    process_disabled = True
if input_mode == "Use stored upload" and selected_stored_path is None:
    process_disabled = True

process_clicked = st.button("Process Document", disabled=process_disabled)

if process_clicked:
    try:
        if input_mode == "Upload new file" and uploaded_file is not None:
            current_input_path = save_uploaded_file(uploaded_file, upload_dir)
        elif input_mode == "Use stored upload" and selected_stored_path is not None:
            current_input_path = selected_stored_path
        else:
            st.error("No valid input document was selected.")
            st.stop()

        processed = process_document_for_preview(current_input_path)
        st.session_state.saved_path = current_input_path
        st.session_state.processed = processed

        stats = processed["stats"]
        chunks = processed["chunks"]
        cleaned_text = processed["clean_text"]

        st.success("Document processed successfully.")

        stat_columns = st.columns(5)
        stat_columns[0].metric("Characters", f"{stats['character_count']:,}")
        stat_columns[1].metric("Words", f"{stats['word_count']:,}")
        stat_columns[2].metric("Paragraphs", f"{stats['paragraph_count']:,}")
        stat_columns[3].metric("Unique words", f"{stats['unique_word_count']:,}")
        stat_columns[4].metric("Reading time", f"{stats['estimated_reading_minutes']} min")

        if is_text_too_short(cleaned_text):
            st.warning(
                "This document is quite short. Future learning-guide generation may work better with more text."
            )

        st.write(f"Generated chunks: **{len(chunks)}**")

        with st.expander("Cleaned text preview", expanded=True):
            st.text_area(
                "First 1500 characters",
                cleaned_text[:1500],
                height=260,
                disabled=True,
            )

        with st.expander("First chunk preview"):
            first_chunk = chunks[0] if chunks else ""
            st.text_area("Chunk 1", first_chunk, height=260, disabled=True)

        st.caption(f"Current input path: `{current_input_path}`")
    except Exception as error:
        st.error(f"Could not process document: {error}")

st.divider()
st.subheader("Stored uploads")

if stored_uploads:
    st.dataframe(build_file_rows(stored_uploads), use_container_width=True)

    for path in stored_uploads:
        row_columns = st.columns([5, 2, 2])
        row_columns[0].write(path.name)
        row_columns[1].write(f"{round(path.stat().st_size / 1024)} KB")
        if row_columns[2].button("Delete", key=f"delete_upload_{path.name}"):
            was_active_input = st.session_state.saved_path == path
            delete_file(path)
            if was_active_input:
                reset_processed_state()
            st.rerun()
else:
    st.caption("No uploaded source files are currently stored.")

st.divider()
st.subheader("PDF Learning Guide")
st.write(
    "Generate a static PDF guide from the uploaded document. LLM providers generate the learning sections. "
    "The guide does not create sentence-wise translation or interactive exercises."
)

provider_order_label = " -> ".join(provider.title() for provider in settings.provider_order)
st.caption(f"Configured provider order: {provider_order_label}")

polish_final_guide = st.checkbox("Polish the final guide with an extra LLM editing pass", value=False)
st.caption(
    "Polishing can improve workbook tone and flow, but it uses several additional LLM calls."
)

st.info(
    "Groq is tried first. Gemini is used automatically when Groq cannot produce a valid section. "
    "The output remains a static PDF."
)

if "groq" in settings.provider_order and not settings.groq_api_key:
    st.warning("GROQ_API_KEY is missing. Add it to `.env` before generating a guide.")
if "gemini" in settings.provider_order and not settings.gemini_api_key:
    st.warning("GEMINI_API_KEY is missing. Add it to `.env` to enable the secondary provider.")

generate_clicked = st.button(
    "Generate PDF Guide",
    disabled=st.session_state.saved_path is None,
)

if generate_clicked and st.session_state.saved_path:
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    table_placeholder = st.empty()

    def update_progress_ui(tracker):
        progress_placeholder.progress(tracker.get_progress_fraction())
        status_placeholder.write(
            f"Completed {tracker.get_completed_count()} of {tracker.get_total_count()} steps."
        )
        table_placeholder.dataframe(tracker.get_display_rows(), use_container_width=True)

    try:
        if not any(
            [
                settings.groq_api_key if "groq" in settings.provider_order else "",
                settings.gemini_api_key if "gemini" in settings.provider_order else "",
            ]
        ):
            st.error("No configured LLM provider API key was found. Add a Groq or Gemini key to `.env`.")
            st.stop()

        result = generate_llm_learning_guide_pdf(
            file_path=st.session_state.saved_path,
            source_language=source_language,
            explanation_language=explanation_language,
            learner_level=learner_level,
            output_dir=output_dir,
            use_llm=True,
            fallback_to_mock_on_section_error=False,
            progress_callback=update_progress_ui,
            polish_final_guide=polish_final_guide,
            fallback_to_unpolished_on_polish_error=False,
        )
        guide = result["guide"]
        pdf_path = result["pdf_path"]
        learning_stats = guide.overview.learning_statistics

        st.success("PDF guide generated successfully.")
        progress_placeholder.progress(1.0)
        table_placeholder.dataframe(result["process_steps"], use_container_width=True)
        st.write(f"Total processing time: **{result['total_duration_seconds']} seconds**")
        st.write("Final polishing enabled: **" + ("yes" if result["polish_final_guide"] else "no") + "**")

        if result["polish_final_guide"]:
            st.write("Polishing succeeded: **" + ("yes" if result["polishing_succeeded"] else "no") + "**")
            if result["polishing_metadata"]:
                rows = [
                    {
                        "section": item.section_name,
                        "provider": item.provider,
                        "model": item.model,
                        "success": item.success,
                    }
                    for item in result["polishing_metadata"]
                ]
                st.dataframe(rows, use_container_width=True)

        sections = result["llm_sections_generated"] or ["None"]
        st.write("LLM-generated sections: " + ", ".join(sections))

        metadata = result.get("generation_metadata")
        if metadata and metadata.sections:
            st.dataframe(metadata.to_display_rows(), use_container_width=True)

        if result["failed_llm_sections"]:
            st.warning("LLM generation failed for: " + ", ".join(result["failed_llm_sections"]))

        stat_columns = st.columns(4)
        stat_columns[0].metric("Vocabulary", learning_stats.vocabulary_count)
        stat_columns[1].metric("Verbs", learning_stats.important_verbs)
        stat_columns[2].metric("Grammar", learning_stats.grammar_concepts)
        stat_columns[3].metric("Exercises", learning_stats.practice_exercises)

        st.write(f"Output file: `{pdf_path.name}`")
        st.download_button(
            "Download PDF Guide",
            data=pdf_path.read_bytes(),
            file_name=pdf_path.name,
            mime="application/pdf",
        )
    except Exception as error:
        st.error(f"Could not generate PDF guide: {error}")

st.divider()
st.subheader("Generated PDFs")

stored_outputs = list_stored_files(output_dir, allowed_suffixes={".pdf"})

if stored_outputs:
    st.dataframe(build_file_rows(stored_outputs), use_container_width=True)

    for path in stored_outputs:
        row_columns = st.columns([4, 2, 2, 2])
        row_columns[0].write(path.name)
        row_columns[1].write(f"{round(path.stat().st_size / 1024)} KB")
        with row_columns[2]:
            st.download_button(
                "Download",
                data=path.read_bytes(),
                file_name=path.name,
                mime="application/pdf",
                key=f"download_output_{path.name}",
            )
        if row_columns[3].button("Delete", key=f"delete_output_{path.name}"):
            delete_file(path)
            st.rerun()
else:
    st.caption("No generated PDF guides are currently stored.")

st.caption("This MVP flow outputs a static PDF learning guide.")
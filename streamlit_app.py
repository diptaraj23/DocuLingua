"""Streamlit entry point for the DocuLingua MVP."""

from __future__ import annotations

import streamlit as st

from app.config import settings
from app.core.document_loader import save_uploaded_file
from app.core.pipeline import generate_llm_learning_guide_pdf, process_document_for_preview
from app.core.text_cleaner import is_text_too_short


st.set_page_config(page_title="DocuLingua", page_icon="DL", layout="centered")

st.title("DocuLingua")
st.caption("Turn a French document into a static PDF learning guide.")

st.write(
    "Upload a PDF or TXT file to extract, clean, chunk, preview, and generate a static PDF learning guide."
)

uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])

source_language = st.selectbox("Source language", ["French"], index=0)
explanation_language = st.selectbox("Explanation language", ["English"], index=0)
learner_level = st.selectbox(
    "Learner level",
    ["Beginner", "Elementary", "Intermediate", "Upper intermediate", "Advanced"],
    index=2,
)

st.divider()

if "saved_path" not in st.session_state:
    st.session_state.saved_path = None
if "processed" not in st.session_state:
    st.session_state.processed = None

if uploaded_file:
    st.info(f"Ready to process: {uploaded_file.name}")
    st.write(
        f"Source: {source_language} | Explanations: {explanation_language} | "
        f"Level: {learner_level}"
    )
else:
    st.info("Upload a PDF or TXT file to start the ingestion preview.")

process_clicked = st.button("Process Document", disabled=uploaded_file is None)

if process_clicked and uploaded_file:
    upload_dir = settings.project_root / "app" / "storage" / "uploads"

    try:
        saved_path = save_uploaded_file(uploaded_file, upload_dir)
        processed = process_document_for_preview(saved_path)
        st.session_state.saved_path = saved_path
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

        st.caption(f"Saved upload locally at: `{saved_path}`")
    except Exception as error:
        st.error(f"Could not process document: {error}")

st.divider()
st.subheader("Sample PDF Guide")
st.write(
    "Generate a static PDF guide. LLM providers can now generate all major PDF learning sections. "
    "The guide does not create sentence-wise translation or interactive exercises."
)
provider_order_label = " -> ".join(provider.title() for provider in settings.provider_order)
st.caption(f"Configured provider order: {provider_order_label}")
use_llm = st.checkbox("Use LLM providers to generate the full learning guide", value=False)
fallback_to_mock = st.checkbox("Use sample fallback if an LLM section fails", value=True)
if use_llm:
    st.info(
        "Groq is tried first. If Groq rate-limits, returns invalid JSON, or produces unusable schema, "
        "the app will try Gemini automatically. The output remains a static PDF."
    )
    if "groq" in settings.provider_order and not settings.groq_api_key:
        st.warning("GROQ_API_KEY is missing. Groq will be skipped and fallback providers may be tried.")
    if "gemini" in settings.provider_order and not settings.gemini_api_key:
        st.warning("GEMINI_API_KEY is missing. Gemini fallback will not be available.")

generate_clicked = st.button(
    "Generate PDF Guide",
    disabled=st.session_state.saved_path is None,
)

if generate_clicked and st.session_state.saved_path:
    output_dir = settings.project_root / "app" / "storage" / "outputs"
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
        if use_llm and not any(
            [
                settings.groq_api_key if "groq" in settings.provider_order else "",
                settings.gemini_api_key if "gemini" in settings.provider_order else "",
            ]
        ):
            st.error("No configured LLM provider API key was found. Add a key to `.env` or disable LLM generation.")
            st.stop()

        result = generate_llm_learning_guide_pdf(
            file_path=st.session_state.saved_path,
            source_language=source_language,
            explanation_language=explanation_language,
            learner_level=learner_level,
            output_dir=output_dir,
            use_llm=use_llm,
            fallback_to_mock_on_section_error=fallback_to_mock,
            progress_callback=update_progress_ui,
        )
        guide = result["guide"]
        pdf_path = result["pdf_path"]
        learning_stats = guide.overview.learning_statistics

        st.success("PDF guide generated successfully.")
        progress_placeholder.progress(1.0)
        table_placeholder.dataframe(result["process_steps"], use_container_width=True)
        st.write(f"Total processing time: **{result['total_duration_seconds']} seconds**")
        st.write("LLM providers used: **" + ("yes" if use_llm else "no") + "**")
        sections = result["llm_sections_generated"] or ["None; mock content used."]
        st.write("LLM-generated sections: " + ", ".join(sections))
        metadata = result.get("generation_metadata")
        if metadata and metadata.sections:
            st.dataframe(metadata.to_display_rows(), use_container_width=True)
        if result["failed_llm_sections"]:
            st.warning("LLM generation failed for: " + ", ".join(result["failed_llm_sections"]))
        if result["used_mock_fallback_sections"]:
            st.warning("Sample fallback used for: " + ", ".join(result["used_mock_fallback_sections"]))
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

st.caption("This MVP flow outputs a static PDF. Disable LLM generation to create a fully mock/sample guide.")

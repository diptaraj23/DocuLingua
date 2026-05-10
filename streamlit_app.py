"""Streamlit entry point for the DocuLingua MVP."""

from __future__ import annotations

import streamlit as st

from app.config import settings
from app.core.document_loader import save_uploaded_file
from app.core.pipeline import generate_mock_learning_guide_pdf, process_document_for_preview
from app.core.text_cleaner import is_text_too_short


st.set_page_config(page_title="DocuLingua", page_icon="DL", layout="centered")

st.title("DocuLingua")
st.caption("Turn a French document into a static PDF learning guide.")

st.write(
    "Upload a PDF or TXT file to extract, clean, chunk, and preview the text. "
    "Groq content generation and PDF export will come in a later phase."
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
    "Generate a static mock PDF guide to test the full workbook flow. "
    "This uses sample content only and does not call Groq yet."
)

generate_clicked = st.button(
    "Generate Sample PDF Guide",
    disabled=st.session_state.saved_path is None,
)

if generate_clicked and st.session_state.saved_path:
    output_dir = settings.project_root / "app" / "storage" / "outputs"

    try:
        result = generate_mock_learning_guide_pdf(
            file_path=st.session_state.saved_path,
            source_language=source_language,
            explanation_language=explanation_language,
            learner_level=learner_level,
            output_dir=output_dir,
        )
        guide = result["guide"]
        pdf_path = result["pdf_path"]
        learning_stats = guide.overview.learning_statistics

        st.success("Sample PDF guide generated successfully.")
        stat_columns = st.columns(4)
        stat_columns[0].metric("Vocabulary", learning_stats.vocabulary_count)
        stat_columns[1].metric("Verbs", learning_stats.important_verbs)
        stat_columns[2].metric("Grammar", learning_stats.grammar_concepts)
        stat_columns[3].metric("Exercises", learning_stats.practice_exercises)

        st.write(f"Output file: `{pdf_path.name}`")
        st.download_button(
            "Download Sample PDF Guide",
            data=pdf_path.read_bytes(),
            file_name=pdf_path.name,
            mime="application/pdf",
        )
    except Exception as error:
        st.error(f"Could not generate sample PDF guide: {error}")

st.caption("This MVP flow uses mock guide content. Groq integration comes later.")

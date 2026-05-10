"""Streamlit entry point for the DocuLingua MVP."""

from __future__ import annotations

import streamlit as st

from app.config import settings
from app.core.document_loader import save_uploaded_file
from app.core.pipeline import process_document_for_preview
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

st.caption("This step only preprocesses documents. It does not call Groq or generate a PDF yet.")

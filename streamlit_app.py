"""Streamlit entry point for the DocuLingua MVP."""

from __future__ import annotations

import streamlit as st

from app.config import settings


st.set_page_config(page_title="DocuLingua", page_icon="DL", layout="centered")

st.title("DocuLingua")
st.caption("Turn a French document into a static PDF learning guide.")

st.write(
    "Upload a PDF or TXT file and DocuLingua will eventually extract the text, "
    "generate language-learning content with Groq, and render a downloadable "
    "PDF workbook. This first version is a scaffold for the MVP workflow."
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
    st.success(f"Ready to process: {uploaded_file.name}")
    st.write(
        f"Source: {source_language} | Explanations: {explanation_language} | "
        f"Level: {learner_level}"
    )
else:
    st.info("Upload a PDF or TXT file to preview the MVP flow.")

st.button("Generate learning guide", disabled=True)

st.caption(
    "Generation is disabled for now. The Groq pipeline and PDF download flow "
    "will be implemented in a later phase."
)

with st.expander("Configuration status"):
    st.write(f"Main Groq model: `{settings.groq_main_model}`")
    st.write(f"Fast Groq model: `{settings.groq_fast_model}`")
    st.write("Groq API key loaded: " + ("yes" if settings.groq_api_key else "no"))

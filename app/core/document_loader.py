"""Document loading helpers for PDF and TXT uploads."""

from __future__ import annotations

from pathlib import Path

import fitz


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def load_txt(path: str | Path, encoding: str = "utf-8") -> str:
    """Read plain text from a TXT file."""

    return Path(path).read_text(encoding=encoding)


def load_pdf(path: str | Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""

    document_path = Path(path)
    text_pages: list[str] = []

    with fitz.open(document_path) as document:
        for page in document:
            text_pages.append(page.get_text())

    return "\n\n".join(text_pages).strip()


def load_document(path: str | Path) -> str:
    """Load supported document text based on the file extension."""

    document_path = Path(path)
    extension = document_path.suffix.lower()

    if extension == ".txt":
        return load_txt(document_path)
    if extension == ".pdf":
        return load_pdf(document_path)

    supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    raise ValueError(f"Unsupported document type '{extension}'. Use: {supported}.")

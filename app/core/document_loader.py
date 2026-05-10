"""Document loading helpers for PDF and TXT uploads."""

from __future__ import annotations

import re
from pathlib import Path

import fitz


SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


def load_txt_file(file_path: Path) -> str:
    """Load text from a UTF-8 encoded TXT file."""

    path = Path(file_path)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise FileNotFoundError(f"TXT file not found: {path}") from error
    except UnicodeDecodeError as error:
        raise ValueError(f"Could not read TXT file as UTF-8: {path}") from error
    except OSError as error:
        raise OSError(f"Could not read TXT file: {path}") from error


def load_pdf_file(file_path: Path) -> str:
    """Extract text from a PDF file using PyMuPDF."""

    path = Path(file_path)
    text_pages: list[str] = []

    try:
        with fitz.open(path) as document:
            for page_number, page in enumerate(document, start=1):
                page_text = page.get_text().strip()
                if page_text:
                    text_pages.append(f"Page {page_number}\n{page_text}")
    except FileNotFoundError as error:
        raise FileNotFoundError(f"PDF file not found: {path}") from error
    except Exception as error:
        raise ValueError(f"Could not extract text from PDF file: {path}") from error

    return "\n\n".join(text_pages).strip()


def load_document(file_path: Path) -> str:
    """Load supported document text based on the file extension."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".txt":
        return load_txt_file(path)
    if extension == ".pdf":
        return load_pdf_file(path)

    supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    raise ValueError(f"Unsupported document type '{extension}'. Use: {supported}.")


def save_uploaded_file(uploaded_file, upload_dir: Path) -> Path:
    """Save a Streamlit uploaded file to a local upload directory."""

    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    original_name = Path(uploaded_file.name).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", original_name).strip("._")
    if not safe_name:
        safe_name = "uploaded_document"

    extension = Path(safe_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported upload type '{extension}'. Use: {supported}.")

    destination = upload_path / safe_name
    stem = destination.stem
    counter = 1
    while destination.exists():
        destination = upload_path / f"{stem}_{counter}{extension}"
        counter += 1

    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def load_txt(path: str | Path, encoding: str = "utf-8") -> str:
    """Backward-compatible alias for loading TXT files."""

    if encoding != "utf-8":
        return Path(path).read_text(encoding=encoding)
    return load_txt_file(Path(path))


def load_pdf(path: str | Path) -> str:
    """Backward-compatible alias for loading PDF files."""

    return load_pdf_file(Path(path))

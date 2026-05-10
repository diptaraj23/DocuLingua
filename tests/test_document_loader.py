from pathlib import Path

import pytest

from app.core.document_loader import load_document, load_txt_file


def test_load_txt_reads_sample_document() -> None:
    sample = Path("data/sample_documents/sample_french_text.txt")

    text = load_txt_file(sample)

    assert "La vieille chanson" in text
    assert "Elise" in text


def test_load_document_rejects_unsupported_extension(tmp_path: Path) -> None:
    sample = tmp_path / "sample.docx"
    sample.write_text("Bonjour", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported document type"):
        load_document(sample)

from pathlib import Path

from app.core.document_loader import load_document, load_txt


def test_load_txt_reads_file(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Bonjour le monde", encoding="utf-8")

    assert load_txt(sample) == "Bonjour le monde"


def test_load_document_rejects_unsupported_extension(tmp_path: Path) -> None:
    sample = tmp_path / "sample.docx"
    sample.write_text("Bonjour", encoding="utf-8")

    try:
        load_document(sample)
    except ValueError as error:
        assert "Unsupported document type" in str(error)
    else:
        raise AssertionError("Expected ValueError for unsupported extension")

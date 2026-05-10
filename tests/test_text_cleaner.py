from app.core.text_chunker import chunk_text
from app.core.text_cleaner import clean_text


def test_clean_text_normalizes_whitespace() -> None:
    assert clean_text("  Bonjour   le monde\n\n\nSalut  ") == "Bonjour le monde\n\nSalut"


def test_chunk_text_splits_text() -> None:
    assert chunk_text("abcdef", max_characters=2) == ["ab", "cd", "ef"]

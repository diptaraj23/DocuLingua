from app.core.text_cleaner import clean_text, is_text_too_short


def test_clean_text_normalizes_whitespace() -> None:
    messy = "  Bonjour   le monde \r\n\r\n\r\n  J'aime   la musique.  "

    assert clean_text(messy) == "Bonjour le monde\n\nJ'aime la musique."


def test_is_text_too_short_detects_short_text() -> None:
    assert is_text_too_short("Bonjour", min_chars=20)
    assert not is_text_too_short("Bonjour le monde. " * 5, min_chars=20)

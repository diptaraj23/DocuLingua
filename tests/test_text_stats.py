from app.core.text_stats import get_text_statistics


def test_text_statistics_contains_expected_keys() -> None:
    stats = get_text_statistics("Bonjour le monde.\n\nBonjour la musique.")

    assert {
        "character_count",
        "word_count",
        "paragraph_count",
        "estimated_reading_minutes",
        "unique_word_count",
    }.issubset(stats)
    assert stats["word_count"] == 6
    assert stats["paragraph_count"] == 2

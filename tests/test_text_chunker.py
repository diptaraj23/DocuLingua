from app.core.text_chunker import chunk_text


def test_long_text_is_split_into_multiple_chunks() -> None:
    text = "\n\n".join(["Bonjour le monde. " * 20 for _ in range(8)])

    chunks = chunk_text(text, max_chars=300, overlap=40)

    assert len(chunks) > 1


def test_chunks_are_non_empty() -> None:
    chunks = chunk_text("Bonjour.\n\nSalut.", max_chars=20, overlap=0)

    assert chunks
    assert all(chunk.strip() for chunk in chunks)


def test_short_text_returns_one_chunk() -> None:
    assert chunk_text("Bonjour le monde.", max_chars=300) == ["Bonjour le monde."]

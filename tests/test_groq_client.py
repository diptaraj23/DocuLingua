from app.llm.groq_client import _parse_json_object


def test_parse_json_object_recovers_last_valid_object() -> None:
    content = """
{
Concept
Definition copied from a table
{
  "summary": "A beginner music guide.",
  "estimated_level": "A2",
  "difficulty_notes": "Clear but topic-specific.",
  "main_learning_focus": ["music vocabulary"],
  "suggested_study_approach": ["review terms"]
}}
"""

    parsed = _parse_json_object(content)

    assert parsed["summary"] == "A beginner music guide."
    assert parsed["main_learning_focus"] == ["music vocabulary"]


def test_generate_json_retries_without_json_mode(monkeypatch) -> None:
    from groq import BadRequestError

    from app.llm.groq_client import GroqClient

    class FakeMessage:
        content = '{"summary": "Recovered from retry"}'

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def __init__(self) -> None:
            self.calls = []

        def create(self, **kwargs):
            self.calls.append(kwargs)
            if "response_format" in kwargs:
                raise BadRequestError(
                    "bad request",
                    response=type(
                        "FakeResponse",
                        (),
                        {"request": None, "status_code": 400, "headers": {}},
                    )(),
                    body={"error": {"message": "json_validate_failed"}},
                )
            return FakeResponse()

    class FakeChat:
        def __init__(self) -> None:
            self.completions = FakeCompletions()

    class FakeGroq:
        def __init__(self) -> None:
            self.chat = FakeChat()

    fake_groq = FakeGroq()
    client = GroqClient(api_key="test-key")
    monkeypatch.setattr(client, "_get_client", lambda: fake_groq)

    parsed = client.generate_json("return JSON")

    assert parsed == {"summary": "Recovered from retry"}
    assert len(fake_groq.chat.completions.calls) == 2
    assert "response_format" not in fake_groq.chat.completions.calls[1]

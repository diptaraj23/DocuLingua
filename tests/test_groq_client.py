from app.llm.response_parser import parse_json_response


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

    parsed = parse_json_response(content)

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


def test_generate_json_uses_structured_output_schema(monkeypatch) -> None:
    from app.llm.groq_client import GroqClient

    class FakeMessage:
        content = '{"items": ["ok"]}'

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def __init__(self) -> None:
            self.calls = []

        def create(self, **kwargs):
            self.calls.append(kwargs)
            return FakeResponse()

    class FakeChat:
        def __init__(self) -> None:
            self.completions = FakeCompletions()

    class FakeGroq:
        def __init__(self) -> None:
            self.chat = FakeChat()

    schema = {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"type": "string"}}},
        "required": ["items"],
        "additionalProperties": False,
    }
    fake_groq = FakeGroq()
    client = GroqClient(api_key="test-key")
    monkeypatch.setattr(client, "_get_client", lambda: fake_groq)

    parsed = client.generate_json("return JSON", json_schema=schema, schema_name="test_schema")

    response_format = fake_groq.chat.completions.calls[0]["response_format"]
    assert parsed == {"items": ["ok"]}
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["name"] == "test_schema"
    assert response_format["json_schema"]["strict"] is True
    assert response_format["json_schema"]["schema"] == schema

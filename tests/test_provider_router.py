import pytest

from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.exceptions import LLMInvalidJSONError, LLMProviderError, LLMRateLimitError
from app.llm.providers.router import ProviderRouter


class FakeProvider(BaseLLMProvider):
    def __init__(self, name: str, response=None, error: Exception | None = None) -> None:
        self.name = name
        self.main_model = f"{name}-main"
        self.fast_model = f"{name}-fast"
        self.response = response or {"ok": True}
        self.error = error
        self.calls = 0

    def is_configured(self) -> bool:
        return True

    def generate_json(self, *args, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def test_router_uses_first_provider_when_it_succeeds() -> None:
    groq = FakeProvider("groq", {"value": "groq"})
    gemini = FakeProvider("gemini", {"value": "gemini"})
    router = ProviderRouter([groq, gemini])

    result, metadata = router.generate_json_with_fallback("prompt", "Test Section")

    assert result == {"value": "groq"}
    assert metadata.provider == "groq"
    assert groq.calls == 1
    assert gemini.calls == 0


def test_router_falls_back_after_rate_limit() -> None:
    groq = FakeProvider("groq", error=LLMRateLimitError("rate limit"))
    gemini = FakeProvider("gemini", {"value": "gemini"})
    router = ProviderRouter([groq, gemini])

    result, metadata = router.generate_json_with_fallback("prompt", "Test Section")

    assert result == {"value": "gemini"}
    assert metadata.provider == "gemini"
    assert [attempt.success for attempt in metadata.attempts] == [False, True]


def test_router_falls_back_after_invalid_json() -> None:
    groq = FakeProvider("groq", error=LLMInvalidJSONError("bad json"))
    gemini = FakeProvider("gemini", {"value": "gemini"})
    router = ProviderRouter([groq, gemini])

    result, metadata = router.generate_json_with_fallback("prompt", "Test Section")

    assert result == {"value": "gemini"}
    assert metadata.attempts[0].error_type == "LLMInvalidJSONError"


def test_router_falls_back_after_validation_failure() -> None:
    groq = FakeProvider("groq", {"wrong": True})
    gemini = FakeProvider("gemini", {"expected": True})
    router = ProviderRouter([groq, gemini])

    def validator(payload):
        if "expected" not in payload:
            raise ValueError("missing expected")
        return payload

    result, metadata = router.generate_validated_json_with_fallback("prompt", "Test Section", validator)

    assert result == {"expected": True}
    assert metadata.provider == "gemini"
    assert metadata.attempts[0].error_type == "LLMValidationError"


def test_router_raises_when_all_providers_fail() -> None:
    router = ProviderRouter(
        [
            FakeProvider("groq", error=LLMInvalidJSONError("bad json")),
            FakeProvider("gemini", error=LLMProviderError("api down")),
        ]
    )

    with pytest.raises(LLMProviderError, match="All LLM providers failed"):
        router.generate_json_with_fallback("prompt", "Test Section")

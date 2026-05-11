"""Provider-level exceptions for LLM generation."""


class LLMProviderError(Exception):
    """Base exception for provider failures."""


class LLMRateLimitError(LLMProviderError):
    """Raised when a provider reports rate limiting."""


class LLMInvalidJSONError(LLMProviderError):
    """Raised when a provider response cannot be parsed as usable JSON."""


class LLMValidationError(LLMProviderError):
    """Raised when parsed JSON does not validate for a section schema."""


class LLMProviderNotConfiguredError(LLMProviderError):
    """Raised when a provider is selected but missing required configuration."""

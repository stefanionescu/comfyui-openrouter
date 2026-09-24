"""Errors that can be shown without exposing provider data."""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable categories for the messages a person sees."""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    CREDITS = "credits"
    INVALID_INPUT = "invalid_input"
    REFUSED = "refused"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    TRANSPORT = "transport"
    UNCERTAIN = "uncertain"
    INTERRUPTED = "interrupted"
    CONFLICT = "conflict"
    DISCOVERY = "models"
    MEDIA = "media"


class ConnectorError(RuntimeError):
    """Show reviewed text; OpenRouter's cleaned reason, when there is one, is already part of it."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        """Store the complete message and its category."""
        super().__init__(message)
        self.code = code


__all__ = ["ConnectorError", "ErrorCode"]

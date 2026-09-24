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
    """Show reviewed text; keep OpenRouter's cleaned reason beside it."""

    def __init__(self, code: ErrorCode, message: str, *, diagnostic_detail: str = "") -> None:
        """Store the complete message, its category, and the cleaned reason it carries."""
        super().__init__(message)
        self.code = code
        self.diagnostic_detail = diagnostic_detail


__all__ = ["ConnectorError", "ErrorCode"]

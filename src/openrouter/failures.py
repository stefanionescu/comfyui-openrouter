"""Turn OpenRouter's error replies into reviewed messages that carry its cleaned reason where it helps."""

import re
import json
from typing import cast
from pydantic import ValidationError
from ..types.replies import ErrorReply
from ..config.openrouter import MAX_REASON_CHARACTERS
from ..types.errors import ErrorCode, OpenRouterError
from ..config.patterns import KEY_PATTERN, URL_PATTERN
from ..config.messages.run import (
    NO_PROVIDER,
    KEY_REJECTED,
    RATE_LIMITED,
    REQUEST_FAILED,
    PROVIDER_FAILED,
    CREDITS_REQUIRED,
    PROVIDER_TIMEOUT,
    REQUEST_REJECTED,
    MODEL_UNAVAILABLE,
    PAYLOAD_TOO_LARGE,
    MODERATION_REFUSED,
    PROVIDER_OVERLOADED,
)

KEY = re.compile(KEY_PATTERN)
URL = re.compile(URL_PATTERN)
NO_REASON = "no reason given"
# Statuses whose reason tells the person what to change, such as the durations a video model accepts.
EXPLAINED_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    400: (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    403: (ErrorCode.REFUSED, MODERATION_REFUSED),
    404: (ErrorCode.UNAVAILABLE, MODEL_UNAVAILABLE),
}
FIXED_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    401: (ErrorCode.AUTHENTICATION, KEY_REJECTED),
    402: (ErrorCode.CREDITS, CREDITS_REQUIRED),
    408: (ErrorCode.TIMEOUT, PROVIDER_TIMEOUT),
    413: (ErrorCode.INVALID_INPUT, PAYLOAD_TOO_LARGE),
    429: (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    502: (ErrorCode.UNAVAILABLE, PROVIDER_FAILED),
    503: (ErrorCode.UNAVAILABLE, NO_PROVIDER),
    524: (ErrorCode.TIMEOUT, PROVIDER_TIMEOUT),
    529: (ErrorCode.UNAVAILABLE, PROVIDER_OVERLOADED),
}


def _read_reason(reply: ErrorReply) -> str:
    """Choose the text that names the problem.

    When the provider rejects a request, OpenRouter's message is only "Provider returned error", and the
    provider's own reason is a JSON string in the error's metadata.
    """
    raw = reply.error.metadata.raw if reply.error.metadata else None
    if raw is None:
        return reply.error.message
    try:
        inner = cast("object", json.loads(raw))
    except ValueError:
        inner = None
    document = cast("dict[str, object]", inner) if isinstance(inner, dict) else {}
    nested = document.get("error")
    candidates = (cast("dict[str, object]", nested).get("message") if isinstance(nested, dict) else None,)
    return next((text for text in (*candidates, document.get("message")) if isinstance(text, str)), raw)


def read_failure(status: int, body: bytes) -> OpenRouterError:
    """Map a failed reply to one reviewed message, adding OpenRouter's reason for the statuses that explain."""
    if status in EXPLAINED_FAILURES:
        code, message = EXPLAINED_FAILURES[status]
        try:
            reason = sanitize_reason(_read_reason(ErrorReply.model_validate_json(body)))
        except ValidationError:
            reason = NO_REASON
        return OpenRouterError(code, message.format(reason=reason))
    code, message = FIXED_FAILURES.get(status, (ErrorCode.TRANSPORT, REQUEST_FAILED))
    return OpenRouterError(code, message.format(status=status))


def sanitize_reason(message: str) -> str:
    """Remove the only private details a provider's reason can carry, keys and addresses, and shorten it."""
    text = " ".join(KEY.sub("", URL.sub("", message)).split())
    if len(text) > MAX_REASON_CHARACTERS:
        text = text[: MAX_REASON_CHARACTERS - 1].rstrip() + "…"
    return text or NO_REASON


__all__ = ["read_failure", "sanitize_reason"]

"""Turn OpenRouter's error replies into reviewed messages that carry its cleaned reason where it helps."""

import re
import json
from typing import cast
from http import HTTPStatus
from pydantic import ValidationError
from ..types.replies import ErrorReply
from ..config.patterns import REASON_PATTERNS
from ..types.errors import ErrorCode, OpenRouterError
from ..config.openrouter import REASON_ENDINGS, MAX_REASON_CHARACTERS
from ..config.messages.run import (
    NO_REASON,
    NO_PROVIDER,
    KEY_REJECTED,
    RATE_LIMITED,
    SERVER_FAILED,
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

KEY = re.compile(REASON_PATTERNS["KEY"])
URL = re.compile(REASON_PATTERNS["URL"])
OPENROUTER_URL = re.compile(REASON_PATTERNS["OPENROUTER_URL"])
# Statuses whose reason tells the person what to change, such as the durations a video model accepts, the tokens
# the credit covers, or the data policy no provider meets. Any other 4xx or 5xx status also carries its reason.
EXPLAINED_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    400: (ErrorCode.INVALID_INPUT, REQUEST_REJECTED),
    402: (ErrorCode.CREDITS, CREDITS_REQUIRED),
    403: (ErrorCode.REFUSED, MODERATION_REFUSED),
    404: (ErrorCode.UNAVAILABLE, MODEL_UNAVAILABLE),
    429: (ErrorCode.RATE_LIMITED, RATE_LIMITED),
    502: (ErrorCode.UNAVAILABLE, PROVIDER_FAILED),
    503: (ErrorCode.UNAVAILABLE, NO_PROVIDER),
}
FIXED_FAILURES: dict[int, tuple[ErrorCode, str]] = {
    401: (ErrorCode.AUTHENTICATION, KEY_REJECTED),
    408: (ErrorCode.TIMEOUT, PROVIDER_TIMEOUT),
    413: (ErrorCode.INVALID_INPUT, PAYLOAD_TOO_LARGE),
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


def _choose_failure(status: int) -> tuple[ErrorCode, str]:
    """Choose the category and message of a status: a known one, any refusal, any server failure, or anything else."""
    known = FIXED_FAILURES | EXPLAINED_FAILURES
    if status in known:
        return known[status]
    if HTTPStatus.BAD_REQUEST <= status < HTTPStatus.INTERNAL_SERVER_ERROR:
        return ErrorCode.INVALID_INPUT, REQUEST_REJECTED
    return ErrorCode.TRANSPORT, SERVER_FAILED if status >= HTTPStatus.INTERNAL_SERVER_ERROR else REQUEST_FAILED


def read_failure(status: int, body: bytes) -> OpenRouterError:
    """Map a failed reply to one reviewed message, adding OpenRouter's reason wherever the message has room."""
    code, message = _choose_failure(status)
    try:
        reason = sanitize_reason(_read_reason(ErrorReply.model_validate_json(body)))
    except ValidationError:
        reason = NO_REASON
    return OpenRouterError(code, message.format(reason=reason, status=status))


def sanitize_reason(message: str) -> str:
    """Remove the only private details a provider's reason can carry, keys and addresses, then shorten it.

    OpenRouter's own addresses stay, without the scheme. The reason ends as a sentence, since a message may add its
    next step after it.
    """
    text = " ".join(KEY.sub("", URL.sub("", OPENROUTER_URL.sub(r"\1", message))).split())
    if len(text) > MAX_REASON_CHARACTERS:
        text = text[: MAX_REASON_CHARACTERS - 1].rstrip() + "…"
    if text and not text.endswith(REASON_ENDINGS):
        text += "."
    return text or NO_REASON


__all__ = ["read_failure", "sanitize_reason"]

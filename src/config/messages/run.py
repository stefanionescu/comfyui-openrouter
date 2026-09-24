"""Messages for OpenRouter failures and refusals; a trailing {reason} is OpenRouter's cleaned reason."""

CREDITS_REQUIRED = (
    "Your OpenRouter account or key has no credit left for this request. Add credits at openrouter.ai/credits "
    "or raise the key's limit."
)
KEY_REJECTED = "OpenRouter did not accept the API key. Check the key in OpenRouter settings."
MODEL_REFUSED = "The model refused to answer: {reason}"
MODEL_UNAVAILABLE = "OpenRouter could not serve this model: {reason}"
# Stands in for a reason when OpenRouter gives none.
NO_REASON = "no reason given"
MODERATION_REFUSED = "OpenRouter blocked this request: {reason}"
NO_PROVIDER = (
    "No provider is available for this request. Loosen Request Options if one is connected, try again later, or "
    "choose another model."
)
OPENROUTER_UNREACHABLE = "ComfyUI could not reach OpenRouter. Check the connection and try again."
PAYLOAD_TOO_LARGE = "The request is too large for OpenRouter. Send fewer or smaller files."
# Only the image endpoint documents that a failed provider is not billed, so this makes no billing claim.
PROVIDER_FAILED = "The model's provider failed to answer. Run again or choose another model."
PROVIDER_OVERLOADED = "The model's provider is overloaded. Try again later or choose another model."
PROVIDER_TIMEOUT = "The model's provider took too long to answer. Try again later."
RATE_LIMITED = "OpenRouter is limiting requests. Wait a moment before running again."
REPLY_EMPTY = "OpenRouter's reply held no result. Run again or choose another model."
REPLY_UNREADABLE = "OpenRouter's reply could not be read."
REQUEST_FAILED = "OpenRouter returned HTTP {status}. Try again later."
REQUEST_REJECTED = "OpenRouter refused the request: {reason}"
REQUEST_TIMEOUT = "The request took longer than the request timeout of {seconds} seconds in OpenRouter settings."
REQUEST_UNCERTAIN = (
    "The connection closed before OpenRouter answered. It may have run and billed this request; check "
    "openrouter.ai/activity before running again."
)

__all__ = [
    "CREDITS_REQUIRED",
    "KEY_REJECTED",
    "MODEL_REFUSED",
    "MODEL_UNAVAILABLE",
    "MODERATION_REFUSED",
    "NO_PROVIDER",
    "NO_REASON",
    "OPENROUTER_UNREACHABLE",
    "PAYLOAD_TOO_LARGE",
    "PROVIDER_FAILED",
    "PROVIDER_OVERLOADED",
    "PROVIDER_TIMEOUT",
    "RATE_LIMITED",
    "REPLY_EMPTY",
    "REPLY_UNREADABLE",
    "REQUEST_FAILED",
    "REQUEST_REJECTED",
    "REQUEST_TIMEOUT",
    "REQUEST_UNCERTAIN",
]

"""Messages for OpenRouter failures and refusals; {reason} is OpenRouter's cleaned reason, ending as a sentence."""

ANSWER_CUT = (
    "The model used up max tokens before answering, often on reasoning. Raise max tokens or lower the reasoning effort."
)

ANSWER_FILTERED = "The provider's content filter stopped the answer. Change the prompt, or choose another model."

CREDITS_REQUIRED = (
    "OpenRouter needs more credit for this request: {reason} Add credits at openrouter.ai/credits, raise the key's "
    "limit, or lower max tokens."
)

KEY_REJECTED = "OpenRouter did not accept the API key. Check the key in OpenRouter settings."

MODEL_REFUSED = "The model refused to answer: {reason}"

MODEL_UNAVAILABLE = "OpenRouter could not serve this model: {reason}"

NO_REASON = "no reason given."

MODERATION_REFUSED = "OpenRouter blocked this request: {reason}"

NO_PROVIDER = (
    "No provider can take this request: {reason} Loosen Request Options if one is connected, try again later, or "
    "choose another model."
)

OPENROUTER_UNREACHABLE = "ComfyUI could not reach OpenRouter. Check the connection and try again."

PAYLOAD_TOO_LARGE = "The request is too large for OpenRouter. Send fewer or smaller files."

# Only the image endpoint documents that a failed provider is not billed, so this makes no billing claim.
PROVIDER_FAILED = "The model's provider failed to answer: {reason} Run again, or choose another model."

PROVIDER_OVERLOADED = "The model's provider is overloaded. Try again later or choose another model."

PROVIDER_TIMEOUT = "The model's provider took too long to answer. Try again later."

RATE_LIMITED = "OpenRouter is limiting requests: {reason} Wait a moment before running again."

REPLY_EMPTY = "OpenRouter's reply held no result. Run again or choose another model."

REPLY_UNREADABLE = "OpenRouter's reply could not be read. Run again, or choose another model if it keeps happening."

REQUEST_FAILED = "OpenRouter returned HTTP {status}. Try again later."

REQUEST_REJECTED = "OpenRouter refused the request: {reason}"

REQUEST_TIMEOUT = "The request took longer than the request timeout of {seconds} seconds in OpenRouter settings."

REQUEST_UNCERTAIN = (
    "The connection closed before OpenRouter answered. It may have run and billed this request; check "
    "openrouter.ai/activity before running again."
)

SERVER_FAILED = "OpenRouter failed with HTTP {status}: {reason} Try again later."

__all__ = [
    "ANSWER_CUT",
    "ANSWER_FILTERED",
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
    "SERVER_FAILED",
]

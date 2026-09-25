"""Regular expression text that its owners compile once."""

# OpenRouter's "~" alias prefix and a ":variant" suffix are part of a model ID; OpenRouter decides whether it exists.
MODEL_ID_PATTERN = r"^~?[a-z0-9][a-z0-9._-]{0,119}/[a-z0-9][a-z0-9._:-]{0,159}$"

# A video job ID in OpenRouter's documented format.
JOB_ID_PATTERN = r"^gen-vid-\d+-[0-9A-Za-z]{20}$"

# A two-letter ISO 639-1 language code, as the transcription endpoint takes.
LANGUAGE_PATTERN = r"^[a-z]{2}$"

# A decision question's name.
QUESTION_NAME_PATTERN = r"^[a-z][a-z0-9_]{0,63}$"

# A settings revision, a SHA-256 digest.
REVISION_PATTERN = r"^[a-f0-9]{64}$"

# A provider slug, with its region or variant.
PROVIDER_SLUG_PATTERN = r"^[a-z0-9][a-z0-9./-]{0,63}$"

# Provider reasons are cleaned of keys and addresses before a person sees them. OpenRouter's own addresses, such
# as its credits page, are kept without the scheme.
REASON_PATTERNS = {
    "KEY": r"sk-or-v1-[0-9A-Za-z]+",
    "URL": r"https?://\S+",
    "OPENROUTER_URL": r"https://(openrouter\.ai/\S*?)(?=[.,;:]?(?:\s|$))",
}

__all__ = [
    "JOB_ID_PATTERN",
    "LANGUAGE_PATTERN",
    "MODEL_ID_PATTERN",
    "PROVIDER_SLUG_PATTERN",
    "QUESTION_NAME_PATTERN",
    "REASON_PATTERNS",
    "REVISION_PATTERN",
]

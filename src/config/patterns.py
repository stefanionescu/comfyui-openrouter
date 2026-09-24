"""Regular expression text that its owners compile once."""

# OpenRouter's "~" alias prefix and a ":variant" suffix are part of a model ID; OpenRouter decides whether it exists.
MODEL_ID_PATTERN = r"^~?[a-z0-9][a-z0-9._-]{0,119}/[a-z0-9][a-z0-9._:-]{0,159}$"
JOB_ID_PATTERN = r"^gen-vid-\d+-[0-9A-Za-z]{20}$"
LANGUAGE_PATTERN = r"^[a-z]{2}$"
QUESTION_NAME_PATTERN = r"^[a-z][a-z0-9_]{0,63}$"
REVISION_PATTERN = r"^[a-f0-9]{64}$"
PROVIDER_SLUG_PATTERN = r"^[a-z0-9][a-z0-9./-]{0,63}$"
# Provider reasons are cleaned of keys and addresses before a person sees them.
KEY_PATTERN = r"sk-or-v1-[0-9A-Za-z]+"
URL_PATTERN = r"https?://\S+"

__all__ = [
    "JOB_ID_PATTERN",
    "KEY_PATTERN",
    "LANGUAGE_PATTERN",
    "MODEL_ID_PATTERN",
    "PROVIDER_SLUG_PATTERN",
    "QUESTION_NAME_PATTERN",
    "REVISION_PATTERN",
    "URL_PATTERN",
]

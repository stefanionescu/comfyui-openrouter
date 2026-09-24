"""Limits and prefixes of the local API."""

SETTINGS_PREFIX = "/openrouter/v1"

MODELS_PREFIX = "/openrouter/v1/models"

MAX_JSON_BYTES = 1_048_576

MAX_JSON_DEPTH = 16

MAX_CREDENTIAL_CHARACTERS = 1024

PRIVATE_HEADERS = {"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"}

__all__ = [
    "MAX_CREDENTIAL_CHARACTERS",
    "MAX_JSON_BYTES",
    "MAX_JSON_DEPTH",
    "MODELS_PREFIX",
    "PRIVATE_HEADERS",
    "SETTINGS_PREFIX",
]

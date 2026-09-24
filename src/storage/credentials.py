"""Resolve the OpenRouter key without placing it in public records."""

import os
from pathlib import Path
from .files import read_private
from ..types.credentials import Credential
from ..types.errors import ErrorCode, OpenRouterError
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..config.messages.settings import KEY_EMPTY, KEY_REQUIRED, KEY_UNREADABLE, KEY_WHITESPACE


def parse_credential(value: str) -> Credential:
    """Reject empty, oversized, or whitespace-containing API keys; OpenRouter decides whether a key is valid."""
    if not value or value != value.strip() or len(value) > MAX_CREDENTIAL_CHARACTERS:
        raise OpenRouterError(ErrorCode.CONFIGURATION, KEY_EMPTY.format(maximum=MAX_CREDENTIAL_CHARACTERS))
    if any(character.isspace() for character in value):
        raise OpenRouterError(ErrorCode.CONFIGURATION, KEY_WHITESPACE)
    return Credential(value)


def read_credential(directory: Path) -> Credential:
    """Prefer the server environment over the private saved key."""
    if "OPENROUTER_API_KEY" in os.environ:
        return parse_credential(os.environ["OPENROUTER_API_KEY"])
    path = directory / "credential"
    if path.exists():
        try:
            return parse_credential(read_private(path, max_bytes=MAX_CREDENTIAL_CHARACTERS).decode("utf-8"))
        except (OSError, UnicodeError):
            raise OpenRouterError(ErrorCode.CONFIGURATION, KEY_UNREADABLE) from None
    raise OpenRouterError(ErrorCode.AUTHENTICATION, KEY_REQUIRED)


def credential_source(directory: Path) -> str:
    """Report presence and source without reading or returning the secret."""
    if "OPENROUTER_API_KEY" in os.environ:
        return "environment"
    return "saved" if (directory / "credential").is_file() else "missing"


__all__ = ["credential_source", "parse_credential", "read_credential"]

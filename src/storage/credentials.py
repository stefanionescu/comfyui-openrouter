"""Resolve the OpenRouter key without placing it in public records."""

import os
from pathlib import Path
from .files import read_file
from ..types.credentials import Credential
from ..types.errors import ErrorCode, OpenRouterError
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..config.storage import ENVIRONMENT_VARIABLES, FILE_NAMES
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
    if ENVIRONMENT_VARIABLES["KEY"] in os.environ:
        return parse_credential(os.environ[ENVIRONMENT_VARIABLES["KEY"]])
    path = directory / FILE_NAMES["CREDENTIAL"]
    if path.exists():
        try:
            return parse_credential(read_file(path, max_bytes=MAX_CREDENTIAL_CHARACTERS).decode("utf-8"))
        except (OSError, UnicodeError):
            raise OpenRouterError(ErrorCode.CONFIGURATION, KEY_UNREADABLE) from None
    raise OpenRouterError(ErrorCode.AUTHENTICATION, KEY_REQUIRED)


def read_credential_source(directory: Path) -> str:
    """Report presence and source without reading or returning the secret."""
    if ENVIRONMENT_VARIABLES["KEY"] in os.environ:
        return "environment"
    return "saved" if (directory / FILE_NAMES["CREDENTIAL"]).is_file() else "missing"


__all__ = ["parse_credential", "read_credential", "read_credential_source"]

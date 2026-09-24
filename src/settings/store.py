"""Own private settings and key changes outside ComfyUI's public storage."""

import json
import secrets
import threading
from ..types import Json
from pathlib import Path
from dataclasses import asdict, fields
from ..types.credentials import Credential
from ..storage.files import save_file, read_file
from ..types.settings import Settings, Configuration
from .schema import DEFAULT_SETTINGS, parse_settings
from ..types.errors import ErrorCode, OpenRouterError
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..types.parsing import parse_json, validate_fields
from ..config.settings import SETTING_RANGES, MAX_SETTINGS_FILE_BYTES
from ..storage.credentials import parse_credential, read_credential, read_credential_source
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE

EDITABLE_SETTINGS = frozenset(item.name for item in fields(Settings))


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings and key changes."""
        self.directory = directory
        self.lock = threading.Lock()
        # The last snapshot; None after a key is removed or the configuration cannot be read.
        self._previous: Configuration | None = None

    def _build_snapshot(self, settings: Settings, credential: Credential) -> Configuration:
        """Return settings and the key with a cache token renewed only when the key changes.

        No setting changes a successful result, and ComfyUI never caches a failed run, so a settings change needs
        no new token.
        """
        previous = self._previous
        generation = previous.generation if previous is not None else secrets.token_hex(16)
        if previous is not None and previous.credential != credential:
            generation = secrets.token_hex(16)
        self._previous = Configuration(settings, credential, generation)
        return self._previous

    def read_snapshot(self) -> Configuration:
        """Read effective values together and invalidate unreadable configuration."""
        with self.lock:
            try:
                settings = read_settings(self.directory)
                credential = read_credential(self.directory)
            except OpenRouterError:
                self._previous = None
                raise
            except (OSError, UnicodeError):
                self._previous = None
                raise OpenRouterError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            return self._build_snapshot(settings, credential)

    def read_status(self) -> dict[str, Json]:
        """Describe effective settings and key presence without returning a key."""
        with self.lock:
            settings = read_settings(self.directory)
            source = read_credential_source(self.directory)
        return {
            "settings": asdict(settings),
            "integer_settings": {
                name: {"minimum": definition["minimum"], "maximum": definition["maximum"]}
                for name, definition in SETTING_RANGES.items()
            },
            "credential_limit": MAX_CREDENTIAL_CHARACTERS,
            "revision": settings.revision,
            "credential": {"source": source},
        }

    def save_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise OpenRouterError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current = read_settings(self.directory)
            if revision != current.revision:
                raise OpenRouterError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            save_file(self.directory / "settings.json", (json.dumps(asdict(updated), indent=2) + "\n").encode())
        return self.read_status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a validated secret and return only the effective source."""
        credential = parse_credential(value)
        with self.lock:
            save_file(self.directory / "credential", credential.reveal().encode("utf-8"))
            previous = self._previous
            # A key saved again unchanged keeps the cache, so it causes no second billed request.
            if (
                read_credential_source(self.directory) != "environment"
                and previous
                and previous.credential != credential
            ):
                self._previous = None
        return self.read_status()

    def delete_credential(self) -> dict[str, Json]:
        """Remove only the saved key; the server environment takes precedence."""
        with self.lock:
            (self.directory / "credential").unlink(missing_ok=True)
            if read_credential_source(self.directory) != "environment":
                self._previous = None
        return self.read_status()


def read_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories."""
    path = directory / "settings.json"
    if not path.exists():
        return DEFAULT_SETTINGS
    return parse_settings(validate_fields(parse_json(read_file(path, max_bytes=MAX_SETTINGS_FILE_BYTES).decode())))


__all__ = ["ConfigurationStore", "read_settings"]

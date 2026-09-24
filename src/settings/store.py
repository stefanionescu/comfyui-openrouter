"""Own private settings and key changes outside ComfyUI's public storage."""

import json
import secrets
import threading
from ..types import Json
from pathlib import Path
from dataclasses import asdict, fields
from ..types.credentials import Credential
from .schema import DEFAULT_SETTINGS, parse_settings
from ..types.errors import ErrorCode, OpenRouterError
from ..types.parsing import parse_json, mapping_value
from ..storage.files import atomic_write, read_private
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..types.settings import Settings, ExecutionConfiguration
from ..config.settings import INTEGER_SETTINGS, MAX_SETTINGS_FILE_BYTES
from ..storage.credentials import parse_credential, read_credential, credential_source
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE

EDITABLE_SETTINGS = frozenset(item.name for item in fields(Settings))


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings and key changes."""
        self.directory = directory
        self.lock = threading.Lock()
        # The last snapshot; None after a key is removed or the configuration cannot be read.
        self._previous: ExecutionConfiguration | None = None

    def _build_snapshot(self, settings: Settings, credential: Credential) -> ExecutionConfiguration:
        """Return settings and the key with a cache token renewed only when the key changes.

        No setting changes a successful result, and ComfyUI never caches a failed run, so a settings change needs
        no new token.
        """
        previous = self._previous
        generation = previous.generation if previous is not None else secrets.token_hex(16)
        if previous is not None and previous.credential != credential:
            generation = secrets.token_hex(16)
        self._previous = ExecutionConfiguration(settings, credential, generation)
        return self._previous

    def execution_snapshot(self) -> ExecutionConfiguration:
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

    def status(self) -> dict[str, Json]:
        """Describe effective settings and key presence without returning a key."""
        with self.lock:
            settings = read_settings(self.directory)
            source = credential_source(self.directory)
        return {
            "settings": asdict(settings),
            "integer_settings": {
                name: {"minimum": definition["minimum"], "maximum": definition["maximum"]}
                for name, definition in INTEGER_SETTINGS.items()
            },
            "credential_limit": MAX_CREDENTIAL_CHARACTERS,
            "revision": settings.revision,
            "credential": {"source": source},
        }

    def update_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise OpenRouterError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current = read_settings(self.directory)
            if revision != current.revision:
                raise OpenRouterError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            atomic_write(self.directory / "settings.json", (json.dumps(asdict(updated), indent=2) + "\n").encode())
        return self.status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a validated secret and return only the effective source."""
        credential = parse_credential(value)
        with self.lock:
            atomic_write(self.directory / "credential", credential.reveal().encode("utf-8"))
            previous = self._previous
            # A key saved again unchanged keeps the cache, so it causes no second billed request.
            if credential_source(self.directory) != "environment" and previous and previous.credential != credential:
                self._previous = None
        return self.status()

    def clear_credential(self) -> dict[str, Json]:
        """Remove only the saved key; the server environment takes precedence."""
        with self.lock:
            (self.directory / "credential").unlink(missing_ok=True)
            if credential_source(self.directory) != "environment":
                self._previous = None
        return self.status()


def read_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories."""
    path = directory / "settings.json"
    if not path.exists():
        return DEFAULT_SETTINGS
    return parse_settings(mapping_value(parse_json(read_private(path, max_bytes=MAX_SETTINGS_FILE_BYTES).decode())))


__all__ = ["ConfigurationStore", "read_settings"]

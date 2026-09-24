"""Own private settings and key changes outside ComfyUI's public storage."""

import json
import threading
from ..state import Json
from pathlib import Path
from dataclasses import asdict, fields
from .snapshot import ConfigurationGeneration
from ..errors import ErrorCode, ConnectorError
from .schema import DEFAULT_SETTINGS, parse_settings
from ..state.parsing import parse_json, mapping_value
from ..storage.files import atomic_write, read_private
from ..config.security import MAX_CREDENTIAL_CHARACTERS
from ..state.settings import Settings, ExecutionConfiguration
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
        self._generation = ConfigurationGeneration()

    def execution_snapshot(self) -> ExecutionConfiguration:
        """Read effective values together and invalidate unreadable configuration."""
        with self.lock:
            try:
                settings = read_settings(self.directory)
                credential = read_credential(self.directory)
            except ConnectorError:
                self._generation.previous = None
                raise
            except (OSError, UnicodeError):
                self._generation.previous = None
                raise ConnectorError(ErrorCode.CONFIGURATION, SETTINGS_UNREADABLE) from None
            return self._generation.snapshot(settings, credential)

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
            raise ConnectorError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current = read_settings(self.directory)
            if revision != current.revision:
                raise ConnectorError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            atomic_write(self.directory / "settings.json", (json.dumps(asdict(updated), indent=2) + "\n").encode())
        return self.status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a validated secret and return only the effective source."""
        credential = parse_credential(value)
        with self.lock:
            atomic_write(self.directory / "credential", credential.reveal().encode("utf-8"))
            previous = self._generation.previous
            # A key saved again unchanged keeps the cache, so it causes no second billed request.
            if credential_source(self.directory) != "environment" and previous and previous.credential != credential:
                self._generation.previous = None
        return self.status()

    def clear_credential(self) -> dict[str, Json]:
        """Remove only the saved key; the server environment takes precedence."""
        with self.lock:
            (self.directory / "credential").unlink(missing_ok=True)
            if credential_source(self.directory) != "environment":
                self._generation.previous = None
        return self.status()


def read_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories."""
    path = directory / "settings.json"
    if not path.exists():
        return DEFAULT_SETTINGS
    return parse_settings(mapping_value(parse_json(read_private(path, max_bytes=MAX_SETTINGS_FILE_BYTES).decode())))


__all__ = ["ConfigurationStore", "read_settings"]

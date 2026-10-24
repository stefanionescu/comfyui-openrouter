"""Own private settings and key changes outside ComfyUI's public storage."""

import json
import hashlib
from pathlib import Path
import secrets
import threading
from dataclasses import asdict, fields

from ..state import Json
from .schema import DEFAULT_SETTINGS, parse_settings
from ..state.errors import ErrorCode, OpenRouterError
from ..state.parsing import parse_json, validate_fields
from ..storage.files import read_file, save_file
from ..config.storage import FILE_NAMES, MAX_FILE_BYTES
from ..state.settings import Settings, Configuration
from ..config.security import GENERATION_TOKEN_BYTES, MAX_CREDENTIAL_CHARACTERS
from ..config.settings import SETTING_RANGES
from ..state.credentials import Credential
from ..storage.credentials import read_credential, parse_credential, read_credential_source
from ..config.messages.settings import SETTINGS_CHANGED, SETTING_READ_ONLY, SETTINGS_UNREADABLE

EDITABLE_SETTINGS = frozenset(item.name for item in fields(Settings))


class ConfigurationStore:
    """Serialize local changes across server and executor threads."""

    def __init__(self, directory: Path) -> None:
        """Select private storage and own the lock for settings and key changes."""
        self.directory = directory
        self.lock = threading.Lock()
        # The last configuration a request read; None after someone removes the key or the configuration is unreadable.
        self._previous: Configuration | None = None

    def _build_configuration(self, settings: Settings, credential: Credential) -> Configuration:
        """Return settings and the key with a cache token renewed only when the key changes.

        No setting changes a successful result, and ComfyUI never caches a failed run, so a settings change needs
        no new token.
        """
        previous = self._previous
        generation = previous.generation if previous is not None else secrets.token_hex(GENERATION_TOKEN_BYTES)
        if previous is not None and previous.credential != credential:
            generation = secrets.token_hex(GENERATION_TOKEN_BYTES)
        self._previous = Configuration(settings, credential, generation)
        return self._previous

    def read_configuration(self) -> Configuration:
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
            return self._build_configuration(settings, credential)

    def read_status(self) -> dict[str, Json]:
        """Describe effective settings and key presence without returning a key."""
        with self.lock:
            settings, revision = _read_revised_settings(self.directory)
            source = read_credential_source(self.directory)
        return {
            'settings': asdict(settings),
            'setting_ranges': {
                name: {'minimum': definition['minimum'], 'maximum': definition['maximum']}
                for name, definition in SETTING_RANGES.items()
            },
            'credential_limit': MAX_CREDENTIAL_CHARACTERS,
            'revision': revision,
            'credential': {'source': source},
        }

    def save_settings(self, changes: dict[str, Json], revision: str) -> dict[str, Json]:
        """Apply a validated patch only to the version the editor actually read."""
        if changes.keys() - EDITABLE_SETTINGS:
            raise OpenRouterError(ErrorCode.CONFIGURATION, SETTING_READ_ONLY)
        with self.lock:
            current, current_revision = _read_revised_settings(self.directory)
            if revision != current_revision:
                raise OpenRouterError(ErrorCode.CONFLICT, SETTINGS_CHANGED)
            updated = parse_settings(asdict(current) | changes)
            save_file(self.directory / FILE_NAMES['SETTINGS'], (json.dumps(asdict(updated), indent=2) + '\n').encode())
        return self.read_status()

    def save_credential(self, value: str) -> dict[str, Json]:
        """Save a validated secret and return only the effective source."""
        credential = parse_credential(value)
        with self.lock:
            save_file(self.directory / FILE_NAMES['CREDENTIAL'], credential.value.encode('utf-8'))
            previous = self._previous
            # A key saved again unchanged keeps the cache, so it causes no second billed request.
            if (
                read_credential_source(self.directory) != 'environment'
                and previous
                and previous.credential != credential
            ):
                self._previous = None
        return self.read_status()

    def delete_credential(self) -> dict[str, Json]:
        """Remove only the saved key; the server environment takes precedence."""
        with self.lock:
            (self.directory / FILE_NAMES['CREDENTIAL']).unlink(missing_ok=True)
            if read_credential_source(self.directory) != 'environment':
                self._previous = None
        return self.read_status()


def read_settings(directory: Path) -> Settings:
    """Read settings without creating files or directories."""
    path = directory / FILE_NAMES['SETTINGS']
    if not path.exists():
        return DEFAULT_SETTINGS
    return parse_settings(validate_fields(parse_json(read_file(path, max_bytes=MAX_FILE_BYTES['SETTINGS']).decode())))


def _read_revised_settings(directory: Path) -> tuple[Settings, str]:
    """Read the settings and their revision, which identifies them so a stale window cannot overwrite newer changes."""
    settings = read_settings(directory)
    encoded = json.dumps(asdict(settings), sort_keys=True, separators=(',', ':')).encode()
    return settings, hashlib.sha256(encoded).hexdigest()


__all__ = ['ConfigurationStore', 'read_settings']

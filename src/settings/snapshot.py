"""Identify effective execution changes without exposing a secret-derived value."""

import secrets
from ..state.credentials import Credential
from ..state.settings import Settings, ExecutionConfiguration


class ConfigurationGeneration:
    """Compare private values under the configuration store's lock.

    Attributes:
        previous: The last snapshot; None after a key is removed or configuration cannot be read.

    """

    def __init__(self) -> None:
        """Start without a reusable execution snapshot."""
        self.previous: ExecutionConfiguration | None = None

    def snapshot(self, settings: Settings, credential: Credential) -> ExecutionConfiguration:
        """Return settings and the key with a cache token renewed only when the key changes.

        No setting changes a successful result, and ComfyUI never caches a failed run, so a settings
        change needs no new token.
        """
        previous = self.previous
        generation = previous.generation if previous is not None else secrets.token_hex(16)
        if previous is not None and previous.credential != credential:
            generation = secrets.token_hex(16)
        current = ExecutionConfiguration(settings, credential, generation)
        self.previous = current
        return current


__all__ = ["ConfigurationGeneration"]

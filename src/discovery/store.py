"""Keep the saved model list in memory, promote refreshed lists atomically, and keep one previous copy."""

from __future__ import annotations

import asyncio
import threading
from typing import TYPE_CHECKING
from ..paths import SNAPSHOT_PATH
from ..tasks import wait_shielded
from .choices import build_choices
from .views import build_model_views
from pydantic import ValidationError
from ..serialization import parse_json
from .sources import read_public_models
from .contracts import merge_observations
from ..errors import ErrorCode, ConnectorError
from ..storage import atomic_write, read_private
from ..state.models import Snapshot, SavedModelLists
from ..config.discovery import MAX_LIST_BYTES, LIST_FILE_NAME
from ..config.messages.models import (
    MODEL_LIST_CHANGED,
    MODEL_REFRESH_WAIT,
    MODEL_ROLLBACK_EMPTY,
    MODEL_REFRESH_RUNNING,
)

if TYPE_CHECKING:
    from ..state import Json
    from pathlib import Path
    from collections.abc import Mapping
    from ..state.capabilities import Choice, Endpoint


class ModelStore:
    """Own the saved model list, refresh admission, promotion, and rollback.

    Only this store writes the list file, so memory and disk agree. Node schemas read the choices on
    every definition request, so they stay in memory; a save replaces the whole mapping at once.

    Attributes:
        choices: Each endpoint's models, keyed by ID in ID order.
        is_damaged: Whether the saved file could not be read, so the bundled list is in use.

    """

    def __init__(self, directory: Path) -> None:
        """Read the saved list, or the bundled one before the first refresh or when the saved file is damaged."""
        self._path = directory / LIST_FILE_NAME
        self._lock = threading.Lock()
        self._admission_lock = threading.Lock()
        self._refreshing = False
        self._bundled = Snapshot.model_validate(
            parse_json(SNAPSHOT_PATH.read_text(encoding="utf-8"), max_bytes=MAX_LIST_BYTES)
        )
        self.is_damaged = False
        saved: SavedModelLists | None = None
        try:
            content = read_private(self._path, max_bytes=MAX_LIST_BYTES).decode()
            saved = SavedModelLists.model_validate(parse_json(content, max_bytes=MAX_LIST_BYTES))
        except FileNotFoundError:
            # Before the first refresh there is no saved file, and the bundled list is in use.
            pass
        except (OSError, UnicodeError, ConnectorError, ValidationError):
            # The nodes must still load; the damaged file stays untouched until a refresh replaces it.
            self.is_damaged = True
        self._current = saved.current if saved else self._bundled
        self._previous = saved.previous if saved else None
        self.choices: Mapping[Endpoint, Mapping[str, Choice]] = build_choices(self._current)

    def status(self) -> dict[str, Json]:
        """Describe the list in use, where it came from, and whether a previous list can be restored."""
        with self._lock:
            current, can_rollback, is_damaged = self._current, self._previous is not None, self.is_damaged
        return {
            "revision": current.revision,
            "retrieved_at": current.retrieved_at,
            "is_bundled": current.revision == self._bundled.revision,
            "is_damaged": is_damaged,
            "can_rollback": can_rollback,
            "models": build_model_views(current),
        }

    def preview(self, candidate: Snapshot) -> tuple[str, str]:
        """Merge a candidate with the list in use without saving it, and return both revisions."""
        with self._lock:
            current = self._current
        return current.revision, merge_observations(current, candidate).revision

    async def refresh(self) -> dict[str, Json]:
        """Read the public lists without holding the list lock, and refuse overlapping refreshes."""
        with self._admission_lock:
            if self._refreshing:
                raise ConnectorError(ErrorCode.DISCOVERY, MODEL_REFRESH_RUNNING)
            self._refreshing = True
        try:
            with self._lock:
                revision = self._current.revision
            candidate = await read_public_models()
            # Keep refresh admission until the atomic write has finished, even after cancellation.
            task = asyncio.create_task(asyncio.to_thread(self._promote, candidate, revision))
            if await wait_shielded(task):
                task.exception()
                raise asyncio.CancelledError
            return task.result()
        finally:
            with self._admission_lock:
                self._refreshing = False

    def _promote(self, candidate: Snapshot, revision: str) -> dict[str, Json]:
        """Save a merged list atomically and keep the list it replaces as the previous one."""
        with self._lock:
            if self._current.revision != revision:
                raise ConnectorError(ErrorCode.CONFLICT, MODEL_LIST_CHANGED)
            merged = merge_observations(self._current, candidate)
            previous = self._current if merged.revision != revision else self._previous
            self._save(merged, previous)
        return self.status()

    def rollback(self, revision: str) -> dict[str, Json]:
        """Swap the list in use and the previous one when no refresh is running."""
        with self._lock:
            with self._admission_lock:
                if self._refreshing:
                    raise ConnectorError(ErrorCode.DISCOVERY, MODEL_REFRESH_WAIT)
            if self._current.revision != revision:
                raise ConnectorError(ErrorCode.CONFLICT, MODEL_LIST_CHANGED)
            if self._previous is None:
                raise ConnectorError(ErrorCode.DISCOVERY, MODEL_ROLLBACK_EMPTY)
            self._save(self._previous, self._current)
        return self.status()

    def _save(self, current: Snapshot, previous: Snapshot | None) -> None:
        """Write both lists atomically, then show the new one to the nodes."""
        saved = SavedModelLists(version=1, current=current, previous=previous)
        atomic_write(self._path, (saved.model_dump_json(indent=1) + "\n").encode())
        self._current, self._previous = current, previous
        self.choices = build_choices(current)
        self.is_damaged = False


__all__ = ["ModelStore"]

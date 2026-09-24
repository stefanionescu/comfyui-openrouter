"""Check OpenRouter's public model lists on a schedule without promoting them."""

import time
import asyncio
from aiohttp import web
from .store import ModelStore
from datetime import UTC, datetime
from ..state.settings import Settings
from .sources import read_public_models
from ..config.settings import INTEGER_SETTINGS
from collections.abc import Callable, AsyncIterator
from ..config.messages.models import AUTOMATIC_CHECK_FAILED
from ..config.discovery import CHECK_POLL_SECONDS, CHECK_TIMEOUT_SECONDS


class ModelChecker:
    """Check for model updates with a request timeout and keep the last valid result."""

    def __init__(self, store: ModelStore, settings: Callable[[], Settings]) -> None:
        """Store the list and settings sources and start the schedule without reading anything."""
        self.store = store
        self.settings = settings
        self.last_attempt: float | None = None
        self.checked_at: str | None = None
        self.base_revision: str | None = None
        self.candidate_revision: str | None = None
        self.error: str | None = None
        self.running = False
        self.enabled = False
        self.interval_hours = INTEGER_SETTINGS["model_interval_hours"]["default"]

    async def tick(self) -> None:
        """Honor current settings and retry failures only after the configured interval."""
        if self.running:
            return
        try:
            settings = await asyncio.to_thread(self.settings)
            self.enabled = settings.model_auto_check
            self.interval_hours = settings.model_interval_hours
            if not self.enabled:
                return
            now = time.monotonic()
            if self.last_attempt is not None and now - self.last_attempt < self.interval_hours * 3600:
                return
            self.last_attempt = now
            self.running = True
            async with asyncio.timeout(CHECK_TIMEOUT_SECONDS):
                candidate = await read_public_models()
                base, merged = await asyncio.to_thread(self.store.preview, candidate)
            self.base_revision, self.candidate_revision = base, merged
            self.checked_at = datetime.now(UTC).isoformat()
            self.error = None
        except Exception:  # noqa: BLE001 -- reason: Keep background failures recoverable without exposing provider URLs or response bodies.
            # Provider exceptions can contain URLs or response bodies. The settings
            # and model dialogs need a recovery action, not those private details.
            self.error = AUTOMATIC_CHECK_FAILED
        finally:
            self.running = False

    async def poll_updates(self) -> None:
        """Poll settings and check for updates only when the configured interval expires."""
        while True:
            await self.tick()
            await asyncio.sleep(CHECK_POLL_SECONDS)

    async def lifecycle(self, _app: web.Application) -> AsyncIterator[None]:
        """Start with aiohttp and await cancellation before the host shuts down."""
        task = asyncio.create_task(self.poll_updates(), name="openrouter-model-check")
        try:
            yield
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


__all__ = ["ModelChecker"]

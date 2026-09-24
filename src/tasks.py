"""Wait for owned tasks that must settle even when the caller is cancelled."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


async def wait_shielded[T](task: asyncio.Task[T]) -> bool:
    """Wait until the task settles despite cancellation, and report whether cancellation arrived."""
    cancelled = False
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            cancelled = True
        except Exception:  # noqa: BLE001 -- reason: The caller reads the settled task's failure after resolving cancellation.
            break
    return cancelled


async def owned_io[T](operation: Callable[[], T]) -> T:
    """Finish blocking work already handed to a thread before letting a cancel through."""
    task = asyncio.create_task(asyncio.to_thread(operation))
    if await wait_shielded(task):
        task.exception()
        raise asyncio.CancelledError
    return task.result()


__all__ = ["owned_io", "wait_shielded"]

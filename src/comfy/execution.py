"""Run one paid request with ComfyUI's progress bar, its cancel, and the parallel request limit."""

from __future__ import annotations

import asyncio
import weakref
from ..tasks import owned_io
from typing import TYPE_CHECKING
from ..runtime import get_runtime
from comfy_api.latest import ComfyAPI
from ..errors import ErrorCode, ConnectorError
from ..config.messages.run import REQUEST_TIMEOUT
from ..config.openrouter import CANCELLATION_POLL_SECONDS
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted

if TYPE_CHECKING:
    from comfy_api.latest import io
    from collections.abc import Callable
    from ..execution.operation import Operation

# One call limit per event loop, shared by every node.
_LIMITS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Semaphore] = weakref.WeakKeyDictionary()


async def wait_for_execution[T](task: asyncio.Task[T]) -> T:
    """Forward ComfyUI interruption to the owned preparation or execution task."""
    try:
        while not task.done():
            throw_exception_if_processing_interrupted()
            await asyncio.wait({task}, timeout=CANCELLATION_POLL_SECONDS)
        return await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


def _read_request_limit(capacity: int) -> asyncio.Semaphore:
    """Return the shared request limit of the running event loop.

    ComfyUI runs each queued prompt on a new event loop, so a changed limit applies from the next prompt.
    """
    loop = asyncio.get_running_loop()
    limit = _LIMITS.get(loop)
    if limit is None:
        limit = _LIMITS[loop] = asyncio.Semaphore(capacity)
    return limit


async def run_request[Result](
    operation: Operation[Result], build_outputs: Callable[[Result], io.NodeOutput]
) -> io.NodeOutput:
    """Validate, send within the parallel limit, and build the node's outputs, showing only ComfyUI's progress bar.

    Building the outputs decodes media, which blocks, so it runs in a worker thread.
    """
    progress = ComfyAPI().execution
    await progress.set_progress(0, 3)
    configuration = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
    operation.validate(configuration.settings)
    await progress.set_progress(1, 3)
    try:
        async with _read_request_limit(configuration.settings.parallel_requests):
            result = await wait_for_execution(asyncio.create_task(operation.send(configuration)))
        await progress.set_progress(2, 3)
        outputs = await owned_io(lambda: build_outputs(result))
        await progress.set_progress(3, 3)
    except ConnectorError as error:
        if error.code is ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        seconds = configuration.settings.request_timeout_seconds
        raise ConnectorError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds)) from None
    return outputs


__all__ = ["run_request", "wait_for_execution"]

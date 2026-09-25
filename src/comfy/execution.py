"""Run paid requests with ComfyUI's progress bar and its cancel."""

from __future__ import annotations

import asyncio
from .runtime import get_runtime
from typing import TYPE_CHECKING
from comfy_api.latest import ComfyAPI
from ..config.messages.run import REQUEST_TIMEOUT
from ..types.errors import ErrorCode, OpenRouterError
from ..config.openrouter import PROGRESS_STEPS, CANCELLATION_POLL_SECONDS
from comfy.model_management import InterruptProcessingException, throw_exception_if_processing_interrupted

if TYPE_CHECKING:
    from comfy_api.latest import io
    from collections.abc import Callable
    from ..openrouter.operation import Operation


async def _wait_shielded[T](task: asyncio.Task[T]) -> bool:
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


async def wait_for_thread[T](work: Callable[[], T]) -> T:
    """Run blocking work in a thread, and finish it before letting a cancel through."""
    task = asyncio.create_task(asyncio.to_thread(work))
    if await _wait_shielded(task):
        task.exception()
        raise asyncio.CancelledError
    return task.result()


async def wait_for_task[T](task: asyncio.Task[T]) -> T:
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


async def send_request[Result](
    operation: Operation[Result], build_outputs: Callable[[Result], io.NodeOutput], node_id: str | None
) -> io.NodeOutput:
    """Validate, send, and build the node's outputs, showing only ComfyUI's progress bar.

    The bar is the node's own: a node that another node calls has no ID, so it leaves the calling node's bar alone.
    Building the outputs decodes media, which blocks, so it runs in a worker thread.
    """
    progress = ComfyAPI().execution
    if node_id is not None:
        await progress.set_progress(0, PROGRESS_STEPS, node_id=node_id)
    configuration = await asyncio.to_thread(get_runtime().configuration.read_snapshot)
    operation.validate(configuration.settings)
    if node_id is not None:
        await progress.set_progress(1, PROGRESS_STEPS, node_id=node_id)
    try:
        result = await wait_for_task(asyncio.create_task(operation.send(configuration)))
        if node_id is not None:
            await progress.set_progress(2, PROGRESS_STEPS, node_id=node_id)
        outputs = await wait_for_thread(lambda: build_outputs(result))
        if node_id is not None:
            await progress.set_progress(PROGRESS_STEPS, PROGRESS_STEPS, node_id=node_id)
    except OpenRouterError as error:
        if error.code is ErrorCode.INTERRUPTED:
            raise InterruptProcessingException from None
        raise
    except TimeoutError:
        seconds = configuration.settings.request_timeout_seconds
        raise OpenRouterError(ErrorCode.TIMEOUT, REQUEST_TIMEOUT.format(seconds=seconds)) from None
    return outputs


__all__ = ["send_request", "wait_for_task", "wait_for_thread"]

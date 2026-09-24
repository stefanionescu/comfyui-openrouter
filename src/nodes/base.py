"""Share the cache key and the run-number input across the paid nodes."""

import asyncio
from typing import ClassVar
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from collections.abc import Callable, Awaitable
from ..config.generation.inputs import VARIATION_INPUT


class PaidNode(io.ComfyNode):
    """Own the cache key and the run-number input every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]

    @classmethod
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the key's token to the cache key, so a new key runs the node again."""
        snapshot = await asyncio.to_thread(get_runtime().configuration.execution_snapshot)
        return snapshot.generation

    @classmethod
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and send."""
        inputs.pop(VARIATION_INPUT, None)
        return await cls.send(**inputs)


__all__ = ["PaidNode"]

"""Share the cache key, the run-number input, and list inputs across the paid nodes."""

import asyncio
from comfy_api.latest import io
from typing import cast, ClassVar
from ..comfy.runtime import get_runtime
from collections.abc import Callable, Awaitable
from ..config.messages.inputs import SINGLE_VALUE
from ..types.errors import ErrorCode, OpenRouterError
from ..config.generation.inputs import RUN_NUMBER_INPUT


class PaidNode(io.ComfyNode):
    """Own the cache key and the run-number input every paid node shares.

    Attributes:
        send: Typed entry point that receives every saved input except the run number.
        list_inputs: The media inputs of a node that takes input lists; each reaches send as the whole list, and
            every other input as its one value.

    """

    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]
    list_inputs: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the key's token to the cache key, so a new key runs the node again."""
        snapshot = await asyncio.to_thread(get_runtime().configuration.read_snapshot)
        return snapshot.generation

    @classmethod
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and send.

        A node that takes input lists receives every input as a list; only its media inputs may hold several items.
        """
        inputs.pop(RUN_NUMBER_INPUT, None)
        if cls.list_inputs:
            for name, value in inputs.items():
                if name not in cls.list_inputs:
                    inputs[name] = _read_single(name, value)
        return await cls.send(**inputs)


def _read_single(name: str, value: object) -> object:
    """Take the one value an input list holds; a dynamic dropdown holds one list for each of its fields."""
    if isinstance(value, dict):
        fields = cast("dict[str, object]", value)
        return {field: _read_single(name, item) for field, item in fields.items()}
    values = cast("list[object]", value)
    if len(values) != 1:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name=name.replace("_", " ")))
    return values[0]


__all__ = ["PaidNode"]

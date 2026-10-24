"""Share the cache key, the request inputs, list inputs, and default or custom dropdowns across the paid nodes."""

from typing import ClassVar, cast, override
import asyncio
from collections.abc import Callable, Awaitable

from comfy_api.latest import io

from ..state.errors import ErrorCode, OpenRouterError
from ..comfy.runtime import get_runtime
from ..config.namespace import SOCKET_TYPES
from ..config.messages.inputs import SINGLE_VALUE
from ..config.generation.inputs import SEED, RUN_NUMBER, INPUT_NAMES, VALUE_CHOICE


class PaidNode(io.ComfyNode):
    """Own the cache key and the run-number input every paid node shares.

    Attributes:
        record: The record of every saved input except the run number, with one field for each input name.
        send: Typed entry point that receives the record.
        list_inputs: The media inputs of a node that takes input lists; each reaches the record as the whole list,
            and every other input as its one value.
        choice_inputs: The default or custom dropdowns; each reaches the record as its custom value, or None at
            default.

    """

    record: ClassVar[Callable[..., object]]
    send: ClassVar[Callable[..., Awaitable[io.NodeOutput]]]
    list_inputs: ClassVar[frozenset[str]] = frozenset()
    choice_inputs: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    @override
    async def fingerprint_inputs(cls, **_inputs: object) -> str:
        """Add the key's token to the cache key, so a new key runs the node again."""
        configuration = await asyncio.to_thread(get_runtime().configuration.read_configuration)
        return configuration.generation

    @classmethod
    @override
    async def execute(cls, **inputs: object) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] # reason: ComfyUI awaits an async execute.
        """Drop the run number, which ComfyUI uses to invalidate its cache, and send.

        A node that takes input lists receives every input as a list; only its media inputs may hold several items.
        """
        inputs.pop(INPUT_NAMES['RUN_NUMBER'], None)
        if cls.list_inputs:
            for name, value in inputs.items():
                if name not in cls.list_inputs:
                    inputs[name] = _read_single(name, value)
        for name in cls.choice_inputs & inputs.keys():
            choice = cast('dict[str, object]', inputs[name])
            inputs[name] = choice[VALUE_CHOICE['VALUE']] if choice[name] == VALUE_CHOICE['SET'] else None
        return await cls.send(cls.record(**inputs))


def _read_single(name: str, value: object) -> object:
    """Take the one value an input list holds; a dynamic dropdown holds one list for each of its fields."""
    if isinstance(value, dict):
        fields = cast('dict[str, object]', value)
        return {field: _read_single(name, item) for field, item in fields.items()}
    values = cast('list[object]', value)
    if len(values) != 1:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, SINGLE_VALUE.format(name=name))
    return values[0]


def build_request_inputs(*, has_seed: bool) -> list[io.Input]:
    """Build the seed, run number, and options inputs that follow the specific inputs of a paid node."""
    seed = io.Int.Input(
        INPUT_NAMES['SEED'],
        tooltip='Number the model uses to vary its output. Results can change after model updates.',
        default=SEED['DEFAULT'],
        min=0,
        max=SEED['MAX'],
        control_after_generate=True,
    )
    run_number = io.Int.Input(
        INPUT_NAMES['RUN_NUMBER'],
        tooltip='Change this number to send the same request again' + (' with the same seed.' if has_seed else '.'),
        default=RUN_NUMBER['DEFAULT'],
        min=RUN_NUMBER['MIN'],
        max=RUN_NUMBER['MAX'],
    )
    options = io.Custom(SOCKET_TYPES['OPTIONS']).Input(
        INPUT_NAMES['OPTIONS'],
        optional=True,
        tooltip='Connect Request Options to choose providers or pass extra fields.',
    )
    return [seed, run_number, options] if has_seed else [run_number, options]


__all__ = ['PaidNode', 'build_request_inputs']

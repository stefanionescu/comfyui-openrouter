"""Build and read the inputs the paid nodes share: the seed, the run number, the options, and socket rows."""

from __future__ import annotations

from comfy_api.latest import io
from typing import TYPE_CHECKING
from ..config.namespace import OPTIONS_TYPE
from ..config.generation.inputs import (
    MAX_SEED,
    SEED_INPUT,
    DEFAULT_SEED,
    MAX_VARIATION,
    MIN_VARIATION,
    OPTIONS_INPUT,
    VARIATION_INPUT,
    DEFAULT_VARIATION,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


def define_request_inputs(*, has_seed: bool) -> list[io.Input]:
    """Build the seed, run number, and options inputs that follow a paid node's own inputs."""
    seed = io.Int.Input(
        SEED_INPUT,
        display_name="seed",
        tooltip="Number used by the model to vary its output. Results can change after model updates.",
        default=DEFAULT_SEED,
        min=0,
        max=MAX_SEED,
        control_after_generate=True,
    )
    variation = io.Int.Input(
        VARIATION_INPUT,
        display_name="run number",
        tooltip="Change this number to send the same request again. The seed stays as it is.",
        default=DEFAULT_VARIATION,
        min=MIN_VARIATION,
        max=MAX_VARIATION,
    )
    options = io.Custom(OPTIONS_TYPE).Input(
        OPTIONS_INPUT,
        optional=True,
        tooltip="Connect Request Options to choose providers or pass extra fields.",
    )
    return [seed, variation, options] if has_seed else [variation, options]


def read_sockets(slots: Mapping[str, object] | None) -> list[object]:
    """List the connected sockets of a growing row, such as image_1 and image_2, in socket order."""
    values = slots or {}
    ordered = sorted(values.items(), key=lambda item: int(item[0].rsplit("_", 1)[1]))
    return [value for _name, value in ordered if value is not None]


__all__ = ["define_request_inputs", "read_sockets"]

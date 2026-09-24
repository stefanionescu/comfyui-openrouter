"""Build and read the inputs every paid node shares: the model dropdown, the seed, the run number, and options."""

from __future__ import annotations

import re
from comfy_api.latest import io
from typing import TYPE_CHECKING
from ..runtime import get_runtime
from ..config.namespace import OPTIONS_TYPE
from ..config.patterns import MODEL_ID_PATTERN
from ..errors import ErrorCode, ConnectorError
from ..state.capabilities import ModelSelection
from ..config.messages.models import MODEL_UNKNOWN
from ..config.generation.inputs import (
    MAX_SEED,
    SEED_INPUT,
    MODEL_INPUT,
    DEFAULT_SEED,
    MAX_VARIATION,
    MIN_VARIATION,
    OPTIONS_INPUT,
    MODEL_ID_INPUT,
    WRITTEN_CHOICE,
    VARIATION_INPUT,
    DEFAULT_VARIATION,
)

if TYPE_CHECKING:
    from ..state.capabilities import Choice, Endpoint
    from collections.abc import Mapping, Callable, Sequence

MODEL_ID = re.compile(MODEL_ID_PATTERN)


def define_model_input[C: Choice](
    endpoint: Endpoint,
    default_model: str,
    define_children: Callable[[C], list[io.Input]],
    written_children: Sequence[io.Input],
) -> io.DynamicCombo.Input:
    """Build the model dropdown from the saved list: the default model first, then every model by ID.

    Each option shows only the controls its model accepts; the last option takes any written ID with every
    control the endpoint accepts.
    """
    choices = get_runtime().models.choices[endpoint]
    ordered = sorted(choices, key=lambda model_id: (model_id != default_model, model_id))
    options = [io.DynamicCombo.Option(model_id, define_children(choices[model_id])) for model_id in ordered]  # pyright: ignore[reportArgumentType] -- reason: Each endpoint's choices share the one record type its node builds from.
    written = io.String.Input(
        MODEL_ID_INPUT,
        display_name="model ID",
        default="",
        tooltip="Any OpenRouter model ID, including variants such as :nitro.",
    )
    options.append(io.DynamicCombo.Option(WRITTEN_CHOICE, [written, *written_children]))
    return io.DynamicCombo.Input(
        MODEL_INPUT,
        options=options,
        tooltip=(
            "The OpenRouter model. Only the settings this model accepts are shown; "
            "choose other model ID to type any ID."
        ),
    )


def read_model[C: Choice](endpoint: Endpoint, model: Mapping[str, object], kind: type[C]) -> ModelSelection[C]:
    """Read the chosen or written model ID, with what the saved list says it accepts.

    A written ID the saved list does not hold is sent unchanged, and OpenRouter decides whether it exists.
    Each endpoint's list holds one record type, so the kind check only narrows the type.
    """
    chosen = str(model[MODEL_INPUT])
    if chosen == WRITTEN_CHOICE:
        chosen = str(model.get(MODEL_ID_INPUT, "")).strip()
        if MODEL_ID.match(chosen) is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, MODEL_UNKNOWN)
    choice = get_runtime().models.choices[endpoint].get(chosen)
    return ModelSelection(chosen, choice if isinstance(choice, kind) else None)


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


__all__ = ["define_model_input", "define_request_inputs", "read_model"]

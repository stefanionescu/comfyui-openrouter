"""Report what OpenRouter lists for any model, read with the same checks the paid nodes use before paying."""

from __future__ import annotations

import json
import asyncio
from comfy_api.latest import io
from ..comfy.runtime import get_runtime
from ..settings.store import read_settings
from typing import override, TYPE_CHECKING
from ..comfy.execution import wait_for_task
from ..config.namespace import NODE_PREFIX, SHARED_MENU
from ..config.generation.models import DEFAULT_CHAT_MODEL
from ..config.generation.inputs import MODEL_INPUT, MODEL_TOOLTIP
from ..openrouter.models import read_model, read_image_limits, read_video_limits

if TYPE_CHECKING:
    from ..types import Json
    from ..types.models import Model, Limits


def _format_report(model_id: str, model: Model, limits: Limits | None) -> str:
    """Write the listing as JSON; a field with fixed values gets values, a range gets min and max, and a flag {}."""
    fields: dict[str, Json] = {}
    for field in sorted(limits.fields if limits is not None else ()):
        if limits is not None and field in limits.choices:
            fields[field] = {"values": list(limits.choices[field])}
        elif limits is not None and field in limits.ranges:
            low, high = (int(bound) if bound.is_integer() else bound for bound in limits.ranges[field])
            fields[field] = {"min": low, "max": high}
        else:
            fields[field] = {}
    report = {
        "model": model_id,
        "inputs": sorted(model.inputs),
        "outputs": sorted(model.outputs),
        "context_length": model.context_length,
        "max_completion_tokens": model.max_completion_tokens,
        "parameters": sorted(model.parameters),
        "voice_cloning": model.has_voice_cloning,
        "providers": list(model.providers),
        "fields": fields,
    }
    return json.dumps(report, ensure_ascii=False)


async def _read_report(model_id: str) -> io.NodeOutput:
    """Read the model's listing, then its image or video fields, without the key."""
    settings = await asyncio.to_thread(read_settings, get_runtime().configuration.directory)
    model = await read_model(model_id, settings)
    limits = None
    if "image" in model.outputs:
        limits = await read_image_limits(model_id, settings)
    elif "video" in model.outputs:
        limits = await read_video_limits(model_id, model.parameters, settings)
    return io.NodeOutput(_format_report(model_id, model, limits))


class ModelInfo(io.ComfyNode):
    """Report one model's listing; it reads only public listings, so it needs no key and costs nothing."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        """List the model ID and the JSON the node returns."""
        return io.Schema(
            node_id=f"{NODE_PREFIX}{cls.__name__}",
            display_name="Model: Info",
            category=SHARED_MENU,
            description="Show what any OpenRouter model reads, makes, and accepts, as JSON. Free, and needs no key.",
            inputs=[io.String.Input(MODEL_INPUT, default=DEFAULT_CHAT_MODEL, tooltip=MODEL_TOOLTIP)],
            outputs=[io.String.Output("info", display_name="info")],
        )

    @classmethod
    @override
    async def execute(cls, *, model: str) -> io.NodeOutput:  # pyright: ignore[reportIncompatibleMethodOverride] -- reason: ComfyUI calls by schema.
        """Read the model's listings inside an owned task, so ComfyUI's cancel stops the wait."""
        return await wait_for_task(asyncio.create_task(_read_report(model.strip())))


__all__ = ["ModelInfo"]

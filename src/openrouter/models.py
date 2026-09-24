"""Check a model against OpenRouter's public listings before a request is sent; nothing here needs the key."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from .transport import download_listing
from ..config.patterns import MODEL_ID_PATTERN
from ..types.errors import ErrorCode, OpenRouterError
from ..types.models import Model, Limits, ModelReply, ImageModelReply, VideoModelsReply
from ..config.openrouter import (
    MODEL_URL,
    FIELD_NAMES,
    MEDIA_LABELS,
    MODEL_OUTPUTS,
    ENDPOINT_LABELS,
    IMAGE_MODEL_URL,
    VIDEO_MODELS_URL,
)
from ..config.messages.models import (
    MODEL_KIND,
    MODEL_EMPTY,
    MODEL_FIELD,
    MODEL_INPUT,
    MODEL_RANGE,
    MODEL_VALUE,
    MODEL_UNKNOWN,
)

if TYPE_CHECKING:
    from ..types import Json, Endpoint
    from ..types.models import VideoModel
    from ..types.settings import Configuration
    from collections.abc import Mapping, Iterable

MODEL_ID = re.compile(MODEL_ID_PATTERN)
# Each listing is read once per ComfyUI session; an unknown ID is looked up again, since it may be fixed.
_MODELS: dict[str, Model] = {}
_IMAGE_LIMITS: dict[str, Limits | None] = {}
_VIDEO_LIMITS: dict[str, Limits] = {}


def _read_range(value: Json) -> tuple[float, float] | None:
    """Read a range OpenRouter lists as {"min", "max"} or as a pair."""
    if isinstance(value, dict):
        low, high = value.get("min"), value.get("max")
    elif isinstance(value, list) and len(value) == len(("min", "max")):
        low, high = value
    else:
        return None
    if isinstance(low, int | float) and isinstance(high, int | float):
        return float(low), float(high)
    return None


def _build_video_limits(video: VideoModel) -> Limits:
    """Keep the fields, choices, and ranges one video model lists."""
    lists = {
        "resolution": video.supported_resolutions,
        "aspect_ratio": video.supported_aspect_ratios,
        "duration": tuple(str(duration) for duration in video.supported_durations or ()) or None,
    }
    choices = {field: values for field, values in lists.items() if values is not None}
    numbers = {"upscale_factor": _read_range(video.upscale_factor), "creativity": _read_range(video.creativity)}
    ranges = {field: bounds for field, bounds in numbers.items() if bounds is not None}
    flags = {"generate_audio": video.generate_audio, "seed": video.seed}
    fields = {*choices, *ranges, *(video.supported_frame_images or ()), *(name for name, on in flags.items() if on)}
    return Limits(frozenset(fields), choices, ranges)


async def validate_model(
    model_id: str, endpoint: Endpoint, configuration: Configuration, inputs: Iterable[str] = ()
) -> Model:
    """Refuse an ID OpenRouter does not list, a model that makes nothing this endpoint returns, or media it cannot read.

    The inputs are the kinds of media connected: image, video, or audio.
    """
    if not model_id:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_EMPTY)
    model = _MODELS.get(model_id)
    if model is None:
        url = MODEL_URL.format(model_id=model_id)
        reply = await download_listing(url, ModelReply, configuration) if MODEL_ID.match(model_id) else None
        if reply is None:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_UNKNOWN.format(model=model_id))
        listing = reply.model
        model = _MODELS[model_id] = Model(
            inputs=frozenset(listing.architecture.input_modalities),
            outputs=frozenset(listing.architecture.output_modalities),
            parameters=frozenset(parameter for item in listing.endpoints for parameter in item.supported_parameters),
            max_tokens=max((item.max_completion_tokens or 0 for item in listing.endpoints), default=0),
            has_voice_cloning=any(item.supports_voice_cloning for item in listing.endpoints),
        )
    if model.outputs.isdisjoint(MODEL_OUTPUTS[endpoint]):
        kind = ENDPOINT_LABELS[endpoint]
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_KIND.format(model=model_id, kind=kind))
    for kind in inputs:
        if model.inputs and kind not in model.inputs:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_INPUT.format(model=model_id, kind=MEDIA_LABELS[kind]))
    return model


async def read_image_limits(model_id: str, configuration: Configuration) -> Limits | None:
    """Read what an image model's providers accept, or None when OpenRouter lists no image providers for it."""
    if model_id not in _IMAGE_LIMITS:
        url = IMAGE_MODEL_URL.format(model_id=model_id)
        reply = await download_listing(url, ImageModelReply, configuration)
        endpoints = reply.endpoints if reply else ()
        parameters = [item for endpoint in endpoints for item in endpoint.supported_parameters.items()]
        choices: dict[str, tuple[str, ...]] = {}
        ranges: dict[str, tuple[float, float]] = {}
        for field, parameter in parameters:
            if parameter.type == "enum":
                choices[field] = tuple(dict.fromkeys((*choices.get(field, ()), *parameter.values)))
            elif parameter.type == "range" and parameter.min is not None and parameter.max is not None:
                low, high = ranges.get(field, (parameter.min, parameter.max))
                ranges[field] = (min(low, parameter.min), max(high, parameter.max))
        fields = frozenset(field for field, _parameter in parameters)
        _IMAGE_LIMITS[model_id] = Limits(fields, choices, ranges) if fields else None
    return _IMAGE_LIMITS[model_id]


async def read_video_limits(model_id: str, configuration: Configuration) -> Limits | None:
    """Read what a video model accepts from OpenRouter's video list, or None when the list does not name it."""
    if not _VIDEO_LIMITS:
        reply = await download_listing(VIDEO_MODELS_URL, VideoModelsReply, configuration)
        _VIDEO_LIMITS.update({video.id: _build_video_limits(video) for video in (reply.models if reply else ())})
    return _VIDEO_LIMITS.get(model_id)


def validate_limits(model_id: str, limits: Limits, values: Mapping[str, Json]) -> None:
    """Refuse a field the model does not take, a value it does not list, and a number outside its range."""
    for field, value in values.items():
        name = FIELD_NAMES.get(field, field.replace("_", " "))
        if field not in limits.fields:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=model_id, field=name))
        choices = limits.choices.get(field)
        if choices is not None and str(value) not in choices:
            message = MODEL_VALUE.format(model=model_id, field=name, values=", ".join(choices))
            raise OpenRouterError(ErrorCode.INVALID_INPUT, message)
        bounds = limits.ranges.get(field)
        if bounds is not None and isinstance(value, int | float) and not bounds[0] <= value <= bounds[1]:
            low, high = (f"{bound:g}" for bound in bounds)
            message = MODEL_RANGE.format(model=model_id, field=name, minimum=low, maximum=high)
            raise OpenRouterError(ErrorCode.INVALID_INPUT, message)


__all__ = ["read_image_limits", "read_video_limits", "validate_limits", "validate_model"]

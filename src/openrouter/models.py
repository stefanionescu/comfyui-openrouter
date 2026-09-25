"""Check a model against OpenRouter's public listings before a request is sent; nothing here needs the key."""

from __future__ import annotations

import re
import asyncio
import weakref
from typing import cast, TYPE_CHECKING
from .transport import download_listing
from ..config.patterns import MODEL_ID_PATTERN
from ..types.errors import ErrorCode, OpenRouterError
from ..types.models import Model, Limits, ModelReply, ImageModelReply, VideoModelsReply
from ..config.openrouter import LISTING_URLS, FIELD_LABELS, MEDIA_LABELS, MODEL_OUTPUTS, ENDPOINT_LABELS
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
    from ..types.models import VideoModel
    from ..types.settings import Settings
    from ..types import Json, Reply, Endpoint
    from collections.abc import Mapping, Iterable

MODEL_ID = re.compile(MODEL_ID_PATTERN)
# Each listing is read once per ComfyUI session; an unknown ID is looked up again, since it may be fixed.
_MODELS: dict[str, Model] = {}
_IMAGE_LIMITS: dict[str, Limits | None] = {}
_VIDEO_MODELS: dict[str, VideoModel] = {}
# The listing reads in flight on each event loop, keyed by address, which callers asking at the same time share.
_READS: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, dict[str, asyncio.Task[Reply | None]]] = (
    weakref.WeakKeyDictionary()
)


def _delete_read(reads: dict[str, asyncio.Task[Reply | None]], url: str, read: asyncio.Task[Reply | None]) -> None:
    """Drop a finished read, so a later caller reads the listing again when this one kept nothing.

    Its failure already reached every caller still waiting; taking it here keeps a read whose callers all cancelled
    from failing unseen.
    """
    del reads[url]
    if not read.cancelled():
        read.exception()


async def _read_listing[T: Reply](url: str, reply: type[T], settings: Settings) -> T | None:
    """Read one public listing, sharing the read with every caller that asks for it at the same time.

    A task belongs to its event loop, and ComfyUI runs each prompt on a new one, so the reads in flight are kept
    per loop. A caller's cancel leaves the read running for the others.
    """
    reads = _READS.setdefault(asyncio.get_running_loop(), {})
    task = reads.get(url)
    if task is None:
        task = reads[url] = cast(
            "asyncio.Task[Reply | None]", asyncio.create_task(download_listing(url, reply, settings))
        )
        task.add_done_callback(lambda done: _delete_read(reads, url, done))
    return cast("T | None", await asyncio.shield(task))


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


def _build_video_limits(video: VideoModel, parameters: frozenset[str]) -> Limits:
    """Keep the fields, choices, and ranges one video model lists.

    A flag the list leaves empty does not refuse anything: sound stays allowed, and the seed goes when the model's
    providers list it.
    """
    lists = {
        "resolution": video.supported_resolutions,
        "aspect_ratio": video.supported_aspect_ratios,
        "duration": tuple(str(duration) for duration in video.supported_durations or ()) or None,
    }
    choices = {field: values for field, values in lists.items() if values is not None}
    numbers = {"upscale_factor": _read_range(video.upscale_factor), "creativity": _read_range(video.creativity)}
    ranges = {field: bounds for field, bounds in numbers.items() if bounds is not None}
    flags = {
        "generate_audio": video.generate_audio is not False,
        "seed": video.seed if video.seed is not None else "seed" in parameters,
    }
    fields = {*choices, *ranges, *(video.supported_frame_images or ()), *(name for name, on in flags.items() if on)}
    return Limits(frozenset(fields), choices, ranges)


async def read_model(model_id: str, settings: Settings) -> Model:
    """Read what OpenRouter lists for one model, refusing an empty ID and one OpenRouter does not list.

    A length OpenRouter lists as 0 or leaves out is not stated, so it reads as None.
    """
    if not model_id:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_EMPTY)
    if model_id not in _MODELS and MODEL_ID.match(model_id):
        reply = await _read_listing(LISTING_URLS["MODEL"].format(model_id=model_id), ModelReply, settings)
        if reply is not None:
            listing = reply.model
            endpoints = listing.endpoints
            _MODELS[model_id] = Model(
                inputs=frozenset(listing.architecture.input_modalities),
                outputs=frozenset(listing.architecture.output_modalities),
                parameters=frozenset(parameter for item in endpoints for parameter in item.supported_parameters),
                context_length=max((item.context_length for item in endpoints if item.context_length), default=None),
                max_completion_tokens=max(
                    (item.max_completion_tokens for item in endpoints if item.max_completion_tokens), default=None
                ),
                has_voice_cloning=any(item.supports_voice_cloning for item in endpoints),
                providers=tuple(dict.fromkeys(item.tag for item in endpoints if item.tag)),
            )
    model = _MODELS.get(model_id)
    if model is None:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_UNKNOWN.format(model=model_id))
    return model


async def validate_model(model_id: str, endpoint: Endpoint, settings: Settings, inputs: Iterable[str] = ()) -> Model:
    """Refuse a model OpenRouter does not list, one that makes nothing this endpoint returns, or media it cannot read.

    The inputs are the kinds of media connected: image, video, or audio.
    """
    model = await read_model(model_id, settings)
    if model.outputs.isdisjoint(MODEL_OUTPUTS[endpoint]):
        kind = ENDPOINT_LABELS[endpoint]
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_KIND.format(model=model_id, kind=kind))
    for kind in inputs:
        if model.inputs and kind not in model.inputs:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_INPUT.format(model=model_id, kind=MEDIA_LABELS[kind]))
    return model


async def read_image_limits(model_id: str, settings: Settings) -> Limits | None:
    """Read what an image model's providers accept, or None when OpenRouter lists no image providers for it."""
    if model_id not in _IMAGE_LIMITS:
        reply = await _read_listing(LISTING_URLS["IMAGE_MODEL"].format(model_id=model_id), ImageModelReply, settings)
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


async def read_video_limits(model_id: str, parameters: frozenset[str], settings: Settings) -> Limits | None:
    """Read what a video model accepts from OpenRouter's video list, or None when the list does not name it.

    The parameters are the request fields the model's providers list, which settle what the video list leaves empty.
    """
    if not _VIDEO_MODELS:
        reply = await _read_listing(LISTING_URLS["VIDEO_MODELS"], VideoModelsReply, settings)
        _VIDEO_MODELS.update({video.id: video for video in (reply.models if reply else ())})
    video = _VIDEO_MODELS.get(model_id)
    return _build_video_limits(video, parameters) if video is not None else None


def validate_limits(model_id: str, limits: Limits, values: Mapping[str, Json]) -> None:
    """Refuse a field the model does not take, a value it does not list, and a number outside its range."""
    for field, value in values.items():
        name = FIELD_LABELS.get(field, field.replace("_", " "))
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


__all__ = ["read_image_limits", "read_model", "read_video_limits", "validate_limits", "validate_model"]

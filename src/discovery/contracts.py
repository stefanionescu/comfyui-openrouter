"""Validate OpenRouter's public model lists and reduce them to the saved records."""

from __future__ import annotations

import re
import json
import hashlib
from ..state import Json, Reply
from typing import TYPE_CHECKING
from pydantic import Field, ValidationError
from decimal import Decimal, InvalidOperation
from ..config.patterns import MODEL_ID_PATTERN
from ..errors import ErrorCode, ConnectorError
from ..config.discovery import MAX_MODELS, MAX_ADDED_MODELS, SOURCE_RETENTION_DIVISOR
from ..config.messages.models import MODEL_LIST_FORMAT, MODEL_LIST_GROWTH, MODEL_LIST_INCOMPLETE
from ..state.models import (
    Snapshot,
    ModelRecord,
    ImageParameter,
    ImageModelRecord,
    VideoModelRecord,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

MODEL_ID = re.compile(MODEL_ID_PATTERN)


class _Architecture(Reply):
    """The input and output kinds of one model."""

    input_modalities: tuple[str, ...] = ()
    output_modalities: tuple[str, ...] = ()


class _Reasoning(Reply):
    """The reasoning efforts one model accepts."""

    supported_efforts: tuple[str, ...] = ()
    default_effort: str | None = None
    mandatory: bool = False


class _TopProvider(Reply):
    """The output limit of the provider OpenRouter prefers."""

    max_completion_tokens: int | None = None


class _ModelEntry(Reply):
    """One record of the full model list."""

    id: str
    name: str
    created: int
    context_length: int | None = None
    architecture: _Architecture
    supported_parameters: tuple[str, ...] = ()
    reasoning: _Reasoning | None = None
    top_provider: _TopProvider | None = None
    supported_voices: tuple[str, ...] | None = None
    pricing: dict[str, Json] = Field(default_factory=dict[str, Json])
    expiration_date: str | None = None


class _ModelList(Reply):
    """The full model list document."""

    records: tuple[_ModelEntry, ...] = Field(alias="data")


class _ImageParameterEntry(Reply):
    """One image request field as the image list describes it."""

    type: str
    values: tuple[str, ...] = ()
    min: int | None = None
    max: int | None = None


class _ImageEntry(Reply):
    """One record of the image endpoint's list."""

    id: str
    architecture: _Architecture
    supported_parameters: dict[str, _ImageParameterEntry] = Field(default_factory=dict[str, _ImageParameterEntry])
    supports_streaming: bool = False


class _ImageList(Reply):
    """The image endpoint's list document."""

    records: tuple[_ImageEntry, ...] = Field(alias="data")


class _UpscaleRange(Reply):
    """The upscale factors an upscaling model accepts."""

    min: float
    max: float


class _VideoEntry(Reply):
    """One record of the video endpoint's list."""

    id: str
    supported_durations: tuple[int, ...] | None = None
    supported_resolutions: tuple[str, ...] | None = None
    supported_aspect_ratios: tuple[str, ...] | None = None
    supported_sizes: tuple[str, ...] | None = None
    supported_frame_images: tuple[str, ...] | None = None
    generate_audio: bool | None = None
    seed: bool | None = None
    upscale_factor: _UpscaleRange | None = None
    creativity: tuple[float, float] | None = None
    allowed_passthrough_parameters: tuple[str, ...] | None = None
    pricing_skus: dict[str, str] | None = None


class _VideoList(Reply):
    """The video endpoint's list document."""

    records: tuple[_VideoEntry, ...] = Field(alias="data")


def build_snapshot(models: Json, images: Json, videos: Json, retrieved_at: str) -> Snapshot:
    """Validate the three public lists and keep only the fields the extension reads."""
    try:
        model_list = _ModelList.model_validate(models)
        image_list = _ImageList.model_validate(images)
        video_list = _VideoList.model_validate(videos)
    except ValidationError:
        raise ConnectorError(ErrorCode.DISCOVERY, MODEL_LIST_FORMAT) from None
    for records in (model_list.records, image_list.records, video_list.records):
        identities = [record.id for record in records]
        if not 0 < len(identities) <= MAX_MODELS or len(set(identities)) != len(identities):
            raise ConnectorError(ErrorCode.DISCOVERY, MODEL_LIST_FORMAT)
    return seal_snapshot(
        retrieved_at,
        _reduce_models(model_list.records),
        _reduce_images(image_list.records),
        _reduce_videos(video_list.records),
    )


def seal_snapshot(
    retrieved_at: str,
    models: tuple[ModelRecord, ...],
    images: tuple[ImageModelRecord, ...],
    videos: tuple[VideoModelRecord, ...],
) -> Snapshot:
    """Sort each list by ID and name the result by its content, which excludes the reading time."""
    models = tuple(sorted(models, key=lambda record: record.id))
    images = tuple(sorted(images, key=lambda record: record.id))
    videos = tuple(sorted(videos, key=lambda record: record.id))
    content = {
        name: [record.model_dump(mode="json") for record in items]
        for name, items in (("models", models), ("images", images), ("videos", videos))
    }
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":")).encode()
    return Snapshot(
        version=1,
        revision=hashlib.sha256(encoded).hexdigest(),
        retrieved_at=retrieved_at,
        models=models,
        images=images,
        videos=videos,
    )


def merge_observations(previous: Snapshot | None, candidate: Snapshot) -> Snapshot:
    """Keep models the latest lists dropped visible, and refuse a list that grew or shrank too far at once.

    A broken or partial response then cannot replace a good list, and saved workflows that use a withdrawn
    model still load; running one shows OpenRouter's own reason.
    """
    if previous is None:
        return candidate
    previous_ids = {record.id for record in previous.models}
    new_ids = {record.id for record in candidate.models}
    if len(new_ids - previous_ids) > max(MAX_ADDED_MODELS, len(previous_ids)):
        raise ConnectorError(ErrorCode.DISCOVERY, MODEL_LIST_GROWTH)
    observed = sum(record.is_observed for record in previous.models)
    if len(new_ids) < max(1, observed // SOURCE_RETENTION_DIVISOR):
        raise ConnectorError(ErrorCode.DISCOVERY, MODEL_LIST_INCOMPLETE)
    withdrawn = tuple(
        record.model_copy(update={"is_observed": False}) for record in previous.models if record.id not in new_ids
    )
    return seal_snapshot(candidate.retrieved_at, candidate.models + withdrawn, candidate.images, candidate.videos)


def _read_prices(pricing: Mapping[str, Json]) -> dict[str, str]:
    """Keep the price lines that are finite, non-negative decimals; OpenRouter marks variable prices as -1."""
    prices: dict[str, str] = {}
    for line, value in pricing.items():
        if not isinstance(value, str):
            continue
        try:
            amount = Decimal(value)
        except InvalidOperation:
            continue
        if amount.is_finite() and amount >= 0:
            prices[line] = value
    return prices


def _reduce_models(entries: Sequence[_ModelEntry]) -> tuple[ModelRecord, ...]:
    """Keep the fields of the full list the nodes and the dialog read.

    One strange record must not block a whole refresh, so a record with an unusable ID is skipped.
    """
    records: list[ModelRecord] = []
    for entry in entries:
        if MODEL_ID.match(entry.id) is None:
            continue
        reasoning = entry.reasoning or _Reasoning()
        records.append(
            ModelRecord(
                id=entry.id,
                name=entry.name,
                created=entry.created,
                context_length=entry.context_length,
                input_modalities=tuple(sorted(entry.architecture.input_modalities)),
                output_modalities=tuple(sorted(entry.architecture.output_modalities)),
                parameters=tuple(sorted(entry.supported_parameters)),
                efforts=reasoning.supported_efforts,
                default_effort=reasoning.default_effort,
                is_reasoning_mandatory=reasoning.mandatory,
                max_output_tokens=entry.top_provider.max_completion_tokens if entry.top_provider else None,
                voices=entry.supported_voices or (),
                prices=_read_prices(entry.pricing),
                expiration_date=entry.expiration_date,
            )
        )
    return tuple(records)


def _reduce_images(entries: Sequence[_ImageEntry]) -> tuple[ImageModelRecord, ...]:
    """Keep the image list's request fields whose kind the nodes know, skipping records with an unusable ID."""
    records: list[ImageModelRecord] = []
    for entry in entries:
        if MODEL_ID.match(entry.id) is None:
            continue
        parameters = {
            name: ImageParameter.model_validate(
                {"kind": value.type, "values": value.values, "minimum": value.min, "maximum": value.max}
            )
            for name, value in entry.supported_parameters.items()
            if value.type in {"enum", "range", "boolean"}
        }
        records.append(
            ImageModelRecord(
                id=entry.id,
                input_modalities=tuple(sorted(entry.architecture.input_modalities)),
                parameters=dict(sorted(parameters.items())),
                has_streaming=entry.supports_streaming,
            )
        )
    return tuple(records)


def _reduce_videos(entries: Sequence[_VideoEntry]) -> tuple[VideoModelRecord, ...]:
    """Keep the video list's choices and prices, skipping records with an unusable ID."""
    records: list[VideoModelRecord] = []
    for entry in entries:
        if MODEL_ID.match(entry.id) is None:
            continue
        upscale = entry.upscale_factor
        records.append(
            VideoModelRecord(
                id=entry.id,
                durations=entry.supported_durations or (),
                resolutions=entry.supported_resolutions or (),
                aspect_ratios=entry.supported_aspect_ratios or (),
                sizes=entry.supported_sizes or (),
                frame_types=entry.supported_frame_images or (),
                generate_audio=entry.generate_audio,
                has_seed=entry.seed,
                upscale_range=(upscale.min, upscale.max) if upscale else None,
                creativity_range=entry.creativity,
                passthrough=entry.allowed_passthrough_parameters or (),
                prices=_read_prices(dict(entry.pricing_skus or {})),
            )
        )
    return tuple(records)


__all__ = ["build_snapshot", "merge_observations", "seal_snapshot"]

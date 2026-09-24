"""Build what each endpoint's models accept from one saved model list."""

from __future__ import annotations

from typing import TYPE_CHECKING
from types import MappingProxyType
from ..state.capabilities import (
    ChatChoice,
    TextChoice,
    ImageChoice,
    VideoChoice,
    SpeechChoice,
)

if TYPE_CHECKING:
    from ..state.models import Snapshot
    from collections.abc import Mapping
    from ..state.capabilities import Choice, Endpoint

CHAT_OUTPUTS = frozenset({"text", "image", "audio"})
CHAT_INPUTS = frozenset({"image", "file", "audio", "video"})
REFERENCE_KINDS = frozenset({"image", "audio", "video"})
# Models whose only output is one of these reach the node of that endpoint.
SINGLE_OUTPUT_ENDPOINTS: dict[str, Endpoint] = {
    "transcription": "transcription",
    "embeddings": "embeddings",
    "rerank": "rerank",
    "decisions": "decisions",
}


def build_choices(snapshot: Snapshot) -> Mapping[Endpoint, Mapping[str, Choice]]:
    """Map each endpoint to its models' choices, keyed by model ID in ID order."""
    names = {record.id: record.name for record in snapshot.models}
    inputs = {record.id: frozenset(record.input_modalities) for record in snapshot.models}
    ratios = {
        record.id: record.parameters["aspect_ratio"].values
        for record in snapshot.images
        if "aspect_ratio" in record.parameters
    }
    choices: dict[Endpoint, dict[str, Choice]] = {
        endpoint: {}
        for endpoint in ("chat", "images", "videos", "speech", "transcription", "embeddings", "rerank", "decisions")
    }
    for record in snapshot.models:
        outputs = frozenset(record.output_modalities)
        if "text" in outputs and outputs <= CHAT_OUTPUTS:
            choices["chat"][record.id] = ChatChoice(
                id=record.id,
                name=record.name,
                inputs=inputs[record.id] & CHAT_INPUTS,
                outputs=outputs - {"text"},
                efforts=record.efforts,
                default_effort=record.default_effort,
                is_reasoning_mandatory=record.is_reasoning_mandatory,
                max_output_tokens=record.max_output_tokens or None,
                parameters=frozenset(record.parameters),
                image_aspect_ratios=ratios.get(record.id, ()),
            )
        elif record.output_modalities == ("speech",):
            choices["speech"][record.id] = SpeechChoice(record.id, record.name, record.voices)
        elif len(record.output_modalities) == 1 and record.output_modalities[0] in SINGLE_OUTPUT_ENDPOINTS:
            endpoint = SINGLE_OUTPUT_ENDPOINTS[record.output_modalities[0]]
            choices[endpoint][record.id] = TextChoice(record.id, record.name, inputs[record.id])
    for image in snapshot.images:
        references = image.parameters.get("input_references")
        choices["images"][image.id] = ImageChoice(
            id=image.id,
            name=names.get(image.id, image.id),
            parameters=MappingProxyType(dict(image.parameters)),
            max_references=references.maximum or 0 if references else 0,
        )
    for video in snapshot.videos:
        choices["videos"][video.id] = VideoChoice(
            id=video.id,
            name=names.get(video.id, video.id),
            durations=video.durations,
            resolutions=video.resolutions,
            aspect_ratios=video.aspect_ratios,
            frame_types=video.frame_types,
            generate_audio=video.generate_audio,
            has_seed=video.has_seed,
            upscale_range=video.upscale_range,
            creativity_range=video.creativity_range,
            passthrough=video.passthrough,
            reference_types=inputs.get(video.id, frozenset()) & REFERENCE_KINDS,
        )
    return MappingProxyType({endpoint: MappingProxyType(items) for endpoint, items in choices.items()})


__all__ = ["build_choices"]

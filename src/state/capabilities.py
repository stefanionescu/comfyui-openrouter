"""What each model accepts on one endpoint, built from the saved model list for node schemas and checks."""

from typing import Literal
from dataclasses import dataclass
from .models import ImageParameter
from collections.abc import Mapping

type Endpoint = Literal["chat", "images", "videos", "speech", "transcription", "embeddings", "rerank", "decisions"]


@dataclass(frozen=True, slots=True)
class ChatChoice:
    """What one chat model reads, makes, and accepts.

    Attributes:
        id: Model ID.
        name: Display name.
        inputs: Media the model reads: image, file, audio, video.
        outputs: Media the model makes besides text: image, audio.
        efforts: Reasoning efforts the model accepts.
        default_effort: The model's own reasoning effort.
        is_reasoning_mandatory: Whether reasoning cannot be turned off.
        max_output_tokens: Largest output token count, when known.
        parameters: Request fields the model accepts.
        image_aspect_ratios: Aspect ratios of a chat model that also draws images.

    """

    id: str
    name: str
    inputs: frozenset[str]
    outputs: frozenset[str]
    efforts: tuple[str, ...]
    default_effort: str | None
    is_reasoning_mandatory: bool
    max_output_tokens: int | None
    parameters: frozenset[str]
    image_aspect_ratios: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImageChoice:
    """What one image model accepts.

    Attributes:
        id: Model ID.
        name: Display name.
        parameters: Image request fields the model accepts, keyed by field name.
        max_references: Most reference images the model takes.

    """

    id: str
    name: str
    parameters: Mapping[str, ImageParameter]
    max_references: int


@dataclass(frozen=True, slots=True)
class VideoChoice:
    """What one video model accepts.

    Attributes:
        id: Model ID.
        name: Display name.
        durations: Accepted durations in whole seconds.
        resolutions: Accepted resolutions.
        aspect_ratios: Accepted aspect ratios.
        frame_types: Accepted frame images.
        generate_audio: The model's sound default, or None when it makes no sound choice.
        has_seed: Whether the model accepts a seed.
        upscale_range: Lowest and highest upscale factor of an upscaling model.
        creativity_range: Lowest and highest creativity of an upscaling model.
        passthrough: Provider fields OpenRouter passes through.
        reference_types: Media the model takes as references: image, audio, video.

    """

    id: str
    name: str
    durations: tuple[int, ...]
    resolutions: tuple[str, ...]
    aspect_ratios: tuple[str, ...]
    frame_types: tuple[str, ...]
    generate_audio: bool | None
    has_seed: bool | None
    upscale_range: tuple[float, float] | None
    creativity_range: tuple[float, float] | None
    passthrough: tuple[str, ...]
    reference_types: frozenset[str]


@dataclass(frozen=True, slots=True)
class SpeechChoice:
    """What one speech model accepts.

    Attributes:
        id: Model ID.
        name: Display name.
        voices: Voice IDs the model lists.

    """

    id: str
    name: str
    voices: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TextChoice:
    """One transcription, embedding, rank, or decision model.

    Attributes:
        id: Model ID.
        name: Display name.
        inputs: Kinds of input the model reads.

    """

    id: str
    name: str
    inputs: frozenset[str]


type Choice = ChatChoice | ImageChoice | VideoChoice | SpeechChoice | TextChoice


@dataclass(frozen=True, slots=True)
class ModelSelection[C: Choice]:
    """The model a node sends, and what it accepts when the saved list knows it.

    Attributes:
        model_id: The ID sent to OpenRouter, unchanged.
        choice: The model's choice record, or None for a typed ID the saved list does not hold.

    """

    model_id: str
    choice: C | None


# Type aliases are imported by name; __all__ lists runtime names.
__all__ = [
    "ChatChoice",
    "ImageChoice",
    "ModelSelection",
    "SpeechChoice",
    "TextChoice",
    "VideoChoice",
]

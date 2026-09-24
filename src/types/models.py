"""What OpenRouter lists for one model, and what the model check keeps of it."""

from . import Json, Reply
from pydantic import Field
from dataclasses import dataclass
from collections.abc import Mapping


class ModelArchitecture(Reply):
    """What a model reads and makes.

    Attributes:
        input_modalities: What the model reads, such as text, image, file, audio, or video.
        output_modalities: What the model makes, such as text, image, video, or embeddings.

    """

    input_modalities: tuple[str, ...] = ()
    output_modalities: tuple[str, ...] = ()


class ModelEndpoint(Reply):
    """One provider that serves the model.

    Attributes:
        supported_parameters: The request fields this provider accepts.
        max_completion_tokens: The longest answer this provider gives, when it says.
        supports_voice_cloning: Whether this provider copies a voice from a sample.

    """

    supported_parameters: tuple[str, ...] = ()
    max_completion_tokens: int | None = None
    supports_voice_cloning: bool = False


class ModelListing(Reply):
    """One model and the providers that serve it.

    Attributes:
        architecture: What the model reads and makes.
        endpoints: The providers that serve it.

    """

    architecture: ModelArchitecture
    endpoints: tuple[ModelEndpoint, ...] = ()


class ModelReply(Reply):
    """OpenRouter's public listing of one model.

    Attributes:
        model: The model, which OpenRouter sends as data.

    """

    model: ModelListing = Field(alias="data")


class ImageParameter(Reply):
    """One request field an image provider accepts.

    Attributes:
        type: enum for a fixed set of values, range for numbers, or boolean.
        values: The values of an enum field.
        min: The lowest value of a range field.
        max: The highest value of a range field.

    """

    type: str = ""
    values: tuple[str, ...] = ()
    min: float | None = None
    max: float | None = None


class ImageEndpoint(Reply):
    """One provider of an image model.

    Attributes:
        supported_parameters: The fields this provider accepts, keyed by field name.

    """

    supported_parameters: Mapping[str, ImageParameter] = Field(default_factory=dict)


class ImageModelReply(Reply):
    """OpenRouter's public listing of one image model's providers.

    Attributes:
        endpoints: The providers that serve it.

    """

    endpoints: tuple[ImageEndpoint, ...] = ()


class VideoModel(Reply):
    """One video model in OpenRouter's public video list; a field it does not list is None.

    Attributes:
        id: The model ID.
        supported_resolutions: The resolutions it makes.
        supported_aspect_ratios: The aspect ratios it makes.
        supported_durations: The durations it makes, in seconds.
        supported_frame_images: The frames it starts or ends on.
        upscale_factor: The upscale range of an upscaling model, as an object or a pair.
        creativity: The creativity range of an upscaling model, as an object or a pair.
        generate_audio: Whether it can make sound; None when the list does not say.
        seed: Whether it takes a seed; None when the list does not say.

    """

    id: str
    supported_resolutions: tuple[str, ...] | None = None
    supported_aspect_ratios: tuple[str, ...] | None = None
    supported_durations: tuple[int, ...] | None = None
    supported_frame_images: tuple[str, ...] | None = None
    upscale_factor: Json = None
    creativity: Json = None
    generate_audio: bool | None = None
    seed: bool | None = None


class VideoModelsReply(Reply):
    """OpenRouter's public list of video models.

    Attributes:
        models: Every video model, which OpenRouter sends as data.

    """

    models: tuple[VideoModel, ...] = Field(default=(), alias="data")


@dataclass(frozen=True, slots=True)
class Model:
    """What the model check learned about one model.

    Attributes:
        inputs: What the model reads; empty when OpenRouter does not say.
        outputs: What the model makes.
        parameters: The request fields at least one of its providers accepts.
        max_tokens: The longest answer any provider gives, or 0 when none says.
        has_voice_cloning: Whether any provider copies a voice from a sample.

    """

    inputs: frozenset[str]
    outputs: frozenset[str]
    parameters: frozenset[str]
    max_tokens: int
    has_voice_cloning: bool


@dataclass(frozen=True, slots=True)
class Limits:
    """What an image or video model accepts, merged across its providers.

    Attributes:
        fields: Every request field at least one provider accepts.
        choices: The values of each field that takes a fixed set, in OpenRouter's order.
        ranges: The lowest and highest value of each numeric field.

    """

    fields: frozenset[str]
    choices: Mapping[str, tuple[str, ...]]
    ranges: Mapping[str, tuple[float, float]]


__all__ = [
    "ImageEndpoint",
    "ImageModelReply",
    "ImageParameter",
    "Limits",
    "Model",
    "ModelArchitecture",
    "ModelEndpoint",
    "ModelListing",
    "ModelReply",
    "VideoModel",
    "VideoModelsReply",
]

"""What OpenRouter lists for one model, and what the model check keeps of it."""

from dataclasses import dataclass
from collections.abc import Mapping

from pydantic import Field

from . import Json, Reply


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
        tag: The provider's slug, which provider routing takes.
        parameters: The request fields this provider accepts, which OpenRouter sends as supported_parameters.
        context_length: The most tokens this provider reads, when it says.
        max_completion_tokens: The longest answer this provider gives, when it says.
        has_voice_cloning: Whether this provider copies a voice from a sample, which OpenRouter sends as
            supports_voice_cloning.

    """

    tag: str = ''
    parameters: tuple[str, ...] = Field(default=(), alias='supported_parameters')
    context_length: int | None = None
    max_completion_tokens: int | None = None
    has_voice_cloning: bool = Field(default=False, alias='supports_voice_cloning')


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

    model: ModelListing = Field(alias='data')


class ImageParameter(Reply):
    """One request field an image provider accepts.

    Attributes:
        type: enum for a fixed set of values, range for numbers, or boolean.
        values: The values of an enum field.
        min: The lowest value of a range field.
        max: The highest value of a range field.

    """

    type: str = ''
    values: tuple[str, ...] = ()
    min: float | None = None
    max: float | None = None


class ImageEndpoint(Reply):
    """One provider of an image model.

    Attributes:
        parameters: The fields this provider accepts, keyed by field name, which OpenRouter sends as
            supported_parameters.
        allowed_passthrough_parameters: The provider's own options, which go under its slug in provider options.

    """

    parameters: Mapping[str, ImageParameter] = Field(default_factory=dict, alias='supported_parameters')
    allowed_passthrough_parameters: tuple[str, ...] = ()


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
        resolutions: The resolutions it makes, which OpenRouter sends as supported_resolutions.
        aspect_ratios: The aspect ratios it makes, which OpenRouter sends as supported_aspect_ratios.
        durations: The durations it makes, in seconds, which OpenRouter sends as supported_durations.
        frame_images: The frames it starts or ends on, which OpenRouter sends as supported_frame_images.

        upscale_factor: The upscale range of an upscaling model, which OpenRouter sends as an object or a pair.
        creativity: The creativity range of an upscaling model, which OpenRouter sends as an object or a pair.
        generate_audio: Whether it can make sound; None when the list does not say.
        seed: Whether it takes a seed; None when the list does not say.
        allowed_passthrough_parameters: The provider's own options, which go under its slug in provider options.

    """

    id: str
    resolutions: tuple[str, ...] | None = Field(default=None, alias='supported_resolutions')
    aspect_ratios: tuple[str, ...] | None = Field(default=None, alias='supported_aspect_ratios')
    durations: tuple[int, ...] | None = Field(default=None, alias='supported_durations')
    frame_images: tuple[str, ...] | None = Field(default=None, alias='supported_frame_images')
    upscale_factor: Json = None
    creativity: Json = None
    generate_audio: bool | None = None
    seed: bool | None = None
    allowed_passthrough_parameters: tuple[str, ...] = ()


class VideoModelsReply(Reply):
    """OpenRouter's public list of video models.

    Attributes:
        models: Every video model, which OpenRouter sends as data.

    """

    models: tuple[VideoModel, ...] = Field(default=(), alias='data')


class Reasoning(Reply):
    """How one model reasons.

    Attributes:
        efforts: The reasoning efforts the model takes, in OpenRouter's order, which OpenRouter sends as
            supported_efforts; None when it does not say.

    """

    efforts: tuple[str, ...] | None = Field(default=None, alias='supported_efforts')


class ReasoningModel(Reply):
    """One model in OpenRouter's public list of reasoning models.

    Attributes:
        id: The model ID.
        reasoning: How it reasons; None when the list does not say.

    """

    id: str
    reasoning: Reasoning | None = None


class ReasoningModelsReply(Reply):
    """OpenRouter's public list of reasoning models.

    Attributes:
        models: Every reasoning model, which OpenRouter sends as data.

    """

    models: tuple[ReasoningModel, ...] = Field(default=(), alias='data')


@dataclass(frozen=True, slots=True)
class Model:
    """What the model check learned about one model.

    Attributes:
        inputs: What the model reads; empty when OpenRouter does not say.
        outputs: What the model makes.
        parameters: The request fields at least one of its providers accepts.
        efforts: The reasoning efforts it takes, in OpenRouter's order; empty when OpenRouter does not list them.

        context_length: The most tokens any provider reads, or None when none says.
        max_completion_tokens: The longest answer any provider gives, or None when none says.
        has_voice_cloning: Whether any provider copies a voice from a sample.
        providers: The slugs of the providers that serve it, in OpenRouter's order.

    """

    inputs: frozenset[str]
    outputs: frozenset[str]
    parameters: frozenset[str]
    efforts: tuple[str, ...]
    context_length: int | None
    max_completion_tokens: int | None
    has_voice_cloning: bool
    providers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Limits:
    """What an image or video model accepts, merged across its providers.

    Attributes:
        fields: Every request field at least one provider accepts.
        choices: The values of each field that takes a fixed set, in OpenRouter's order.
        ranges: The lowest and highest value of each numeric field.
        options: The providers' own options, which Request Options sends as provider_options under a provider's slug.

    """

    fields: frozenset[str]
    choices: Mapping[str, tuple[str, ...]]
    ranges: Mapping[str, tuple[float, float]]
    options: frozenset[str]


__all__ = [
    'ImageEndpoint',
    'ImageModelReply',
    'ImageParameter',
    'Limits',
    'Model',
    'ModelArchitecture',
    'ModelEndpoint',
    'ModelListing',
    'ModelReply',
    'Reasoning',
    'ReasoningModel',
    'ReasoningModelsReply',
    'VideoModel',
    'VideoModelsReply',
]

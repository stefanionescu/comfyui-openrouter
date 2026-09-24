"""The saved model list: OpenRouter's three public lists, reduced to what the extension reads."""

from . import Value
from typing import Literal
from collections.abc import Mapping


class ModelRecord(Value):
    """One model from OpenRouter's full model list.

    Attributes:
        id: Model ID, such as google/gemini-3.5-flash.
        name: Display name.
        created: Unix seconds when OpenRouter added the model.
        context_length: Context window in tokens, when known.
        input_modalities: Kinds of input the model reads.
        output_modalities: Kinds of output the model makes.
        parameters: Request fields the model accepts.
        efforts: Reasoning efforts the model accepts.
        default_effort: The model's own reasoning effort.
        is_reasoning_mandatory: Whether reasoning cannot be turned off.
        max_output_tokens: Largest output token count, when known.
        voices: Voice IDs of a speech model.
        prices: OpenRouter's decimal prices in US dollars, keyed by price line.
        expiration_date: Date OpenRouter withdraws the model, when set.
        is_observed: False when the latest refresh no longer listed the model.

    """

    id: str
    name: str
    created: int
    context_length: int | None
    input_modalities: tuple[str, ...]
    output_modalities: tuple[str, ...]
    parameters: tuple[str, ...]
    efforts: tuple[str, ...]
    default_effort: str | None
    is_reasoning_mandatory: bool
    max_output_tokens: int | None
    voices: tuple[str, ...]
    prices: Mapping[str, str]
    expiration_date: str | None
    is_observed: bool = True


class ImageParameter(Value):
    """One image request field a model accepts, as OpenRouter describes it.

    Attributes:
        kind: enum for a list of values, range for whole numbers, boolean for a flag.
        values: The values an enum accepts.
        minimum: The lowest value a range accepts.
        maximum: The highest value a range accepts.

    """

    kind: Literal["enum", "range", "boolean"]
    values: tuple[str, ...] = ()
    minimum: int | None = None
    maximum: int | None = None


class ImageModelRecord(Value):
    """One model from the image endpoint's list.

    Attributes:
        id: Model ID.
        input_modalities: Kinds of input the model reads.
        parameters: Image request fields the model accepts, keyed by field name.
        has_streaming: Whether the model can stream partial images.

    """

    id: str
    input_modalities: tuple[str, ...]
    parameters: Mapping[str, ImageParameter]
    has_streaming: bool


class VideoModelRecord(Value):
    """One model from the video endpoint's list.

    Attributes:
        id: Model ID.
        durations: Accepted durations in whole seconds.
        resolutions: Accepted resolutions.
        aspect_ratios: Accepted aspect ratios.
        sizes: Accepted pixel sizes.
        frame_types: Accepted frame images: first_frame, last_frame.
        generate_audio: The model's sound default, or None when it makes no sound choice.
        has_seed: Whether the model accepts a seed, or None when OpenRouter does not say.
        upscale_range: Lowest and highest upscale factor of an upscaling model.
        creativity_range: Lowest and highest creativity of an upscaling model.
        passthrough: Provider fields OpenRouter passes through.
        prices: OpenRouter's price strings keyed by SKU name.

    """

    id: str
    durations: tuple[int, ...]
    resolutions: tuple[str, ...]
    aspect_ratios: tuple[str, ...]
    sizes: tuple[str, ...]
    frame_types: tuple[str, ...]
    generate_audio: bool | None
    has_seed: bool | None
    upscale_range: tuple[float, float] | None
    creativity_range: tuple[float, float] | None
    passthrough: tuple[str, ...]
    prices: Mapping[str, str]


class Snapshot(Value):
    """One validated reading of the three public lists.

    Attributes:
        version: File format version.
        revision: SHA-256 of the canonical lists; reading the same lists twice gives the same value.
        retrieved_at: When the lists were read, in ISO 8601.
        models: The full model list.
        images: The image endpoint's list.
        videos: The video endpoint's list.

    """

    version: Literal[1]
    revision: str
    retrieved_at: str
    models: tuple[ModelRecord, ...]
    images: tuple[ImageModelRecord, ...]
    videos: tuple[VideoModelRecord, ...]


class SavedModelLists(Value):
    """The model list file: the list in use and the one before it.

    Attributes:
        version: File format version.
        current: The list the nodes show.
        previous: The list Restore Previous List brings back.

    """

    version: Literal[1]
    current: Snapshot
    previous: Snapshot | None


__all__ = ["ImageModelRecord", "ImageParameter", "ModelRecord", "SavedModelLists", "Snapshot", "VideoModelRecord"]

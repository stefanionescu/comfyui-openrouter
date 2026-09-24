"""What OpenRouter lists for one model, and what the model check keeps of it."""

from . import Reply
from pydantic import Field
from dataclasses import dataclass


class ModelArchitecture(Reply):
    """What a model reads and makes.

    Attributes:
        output_modalities: What the model makes, such as text, image, video, or embeddings.

    """

    output_modalities: tuple[str, ...] = ()


class ModelEndpoint(Reply):
    """One provider that serves the model.

    Attributes:
        supported_parameters: The request fields this provider accepts.

    """

    supported_parameters: tuple[str, ...] = ()


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


@dataclass(frozen=True, slots=True)
class Model:
    """What the model check learned about one model.

    Attributes:
        outputs: What the model makes.
        parameters: The request fields at least one of its providers accepts.

    """

    outputs: frozenset[str]
    parameters: frozenset[str]


__all__ = ["Model", "ModelArchitecture", "ModelEndpoint", "ModelListing", "ModelReply"]

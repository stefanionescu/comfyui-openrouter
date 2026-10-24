"""Image requests and results."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from collections.abc import Mapping

    from . import Json
    from .options import Options


@dataclass(frozen=True, slots=True)
class ImageRequest:
    """One image request with its references already encoded.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        prompt: What to draw or change.
        reference_urls: Lossless WebP data URLs of the reference images.

        n: How many images to make; the request sends it only above 1.
        width: The exact width in pixels, sent with height as size; 0 sends no size.
        height: The exact height in pixels, sent with width as size; 0 sends no size.
        seed: Seed sent when the model accepts one.
        fields: The chosen request fields under their wire names, only those other than the model's default.
        options: Provider routing and extra fields.

    """

    model_id: str
    prompt: str
    reference_urls: tuple[str, ...]
    n: int
    width: int
    height: int
    seed: int
    fields: Mapping[str, Json]
    options: Options | None


@dataclass(frozen=True, slots=True)
class ImageOutput:
    """One file the image endpoint returned.

    Attributes:
        content: The encoded image.
        media_type: The file's media type; SVG files are always marked image/svg+xml.

    """

    content: bytes
    media_type: str


@dataclass(frozen=True, slots=True)
class ImageResult:
    """Every file one image request returned.

    Attributes:
        outputs: The files in the order OpenRouter sent them.

    """

    outputs: tuple[ImageOutput, ...]


__all__ = ['ImageOutput', 'ImageRequest', 'ImageResult']

"""Send one request to OpenRouter's image endpoint and read the files it returns."""

from __future__ import annotations

import base64
import binascii
from .transport import send_json
from typing import TYPE_CHECKING
from pydantic import ValidationError
from ..types.replies import ImageReply
from .options import build_request_body
from ..config.openrouter import IMAGES_URL
from .operation import validate_upload_size
from ..config.messages.models import MODEL_COUNT
from ..types.images import ImageOutput, ImageResult
from ..config.media import SVG_STARTS, SVG_MEDIA_TYPE
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ..config.messages.inputs import PROMPT_EMPTY, TRANSPARENT_FORMAT
from .models import validate_model, validate_limits, read_image_limits

if TYPE_CHECKING:
    from ..types import Json
    from ..types.models import Limits
    from ..types.images import ImageRequest
    from ..types.settings import Settings, Configuration


class ImageOperation:
    """One image request; a failed one is not billed, since the endpoint bills only completed images."""

    def __init__(self, request: ImageRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty prompt, a transparent JPEG, and too much media."""
        request = self.request
        if not request.prompt.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        if request.fields.get("background") == "transparent" and request.fields.get("output_format") == "jpeg":
            raise OpenRouterError(ErrorCode.INVALID_INPUT, TRANSPARENT_FORMAT)
        validate_upload_size(request.reference_urls, settings)

    def build_fields(self, limits: Limits | None) -> dict[str, Json]:
        """Check the fields, count, and references against the model's image listing when it has one.

        The compression, which always has a value, is left out for a model that does not take it.
        """
        request = self.request
        fields: dict[str, Json] = dict(request.fields)
        if request.count > 1:
            fields["n"] = request.count
        if limits is None:
            return fields
        if "output_compression" not in limits.fields:
            fields.pop("output_compression", None)
        # A model that does not list a count makes one image per request.
        maximum = int(limits.ranges["n"][1]) if "n" in limits.ranges else 1
        if request.count > maximum:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_COUNT.format(model=request.model_id, maximum=maximum))
        checked = {field: value for field, value in fields.items() if field != "n"}
        if request.reference_urls or "input_references" in limits.fields:
            checked["input_references"] = len(request.reference_urls)
        validate_limits(request.model_id, limits, checked)
        return fields

    async def send(self, configuration: Configuration) -> ImageResult:
        """Check the model, send, and read every image; an SVG file is known by its type or its first bytes."""
        request = self.request
        inputs = ["image"] if request.reference_urls else []
        model = await validate_model(request.model_id, "images", configuration, inputs)
        limits = await read_image_limits(request.model_id, configuration)
        body: dict[str, Json] = {"model": request.model_id, "prompt": request.prompt, **self.build_fields(limits)}
        if "seed" in (limits.fields if limits is not None else model.parameters):
            body["seed"] = request.seed
        if request.reference_urls:
            body["input_references"] = [
                {"type": "image_url", "image_url": {"url": url}} for url in request.reference_urls
            ]
        document = await send_json(IMAGES_URL, build_request_body(body, request.options, "images"), configuration)
        try:
            reply = ImageReply.model_validate(document)
            files = [(base64.b64decode(item.b64_json, validate=True), item.media_type) for item in reply.images]
        except (ValidationError, binascii.Error):
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if not files:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_EMPTY)
        return ImageResult(
            tuple(
                ImageOutput(content, SVG_MEDIA_TYPE if content.lstrip().startswith(SVG_STARTS) else media or "")
                for content, media in files
            )
        )


__all__ = ["ImageOperation"]

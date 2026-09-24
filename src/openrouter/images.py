"""Send one request to OpenRouter's image endpoint and read the files it returns."""

from __future__ import annotations

import base64
import binascii
from .models import check_model
from .transport import post_json
from typing import TYPE_CHECKING
from .options import apply_options
from pydantic import ValidationError
from ..state.replies import ImageReply
from .operation import check_upload_size
from ..config.openrouter import IMAGES_URL
from ..errors import ErrorCode, ConnectorError
from ..state.images import ImageOutput, ImageResult
from ..config.media import SVG_STARTS, SVG_MEDIA_TYPE
from ..config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ..config.messages.inputs import PROMPT_EMPTY, TRANSPARENT_FORMAT

if TYPE_CHECKING:
    from ..state import Json
    from ..state.images import ImageRequest
    from ..state.settings import Settings, ExecutionConfiguration


class ImageOperation:
    """One image request; a failed one is not billed, since the endpoint bills only completed images."""

    def __init__(self, request: ImageRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty prompt, a transparent JPEG, and too much media."""
        request = self.request
        if not request.prompt.strip():
            raise ConnectorError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        if request.fields.get("background") == "transparent" and request.fields.get("output_format") == "jpeg":
            raise ConnectorError(ErrorCode.INVALID_INPUT, TRANSPARENT_FORMAT)
        check_upload_size(request.reference_urls, settings)

    async def send(self, configuration: ExecutionConfiguration) -> ImageResult:
        """Check the model, send, and read every image; an SVG file is known by its type or its first bytes."""
        request = self.request
        model = await check_model(request.model_id, "images", configuration)
        body: dict[str, Json] = {"model": request.model_id, "prompt": request.prompt, **request.fields}
        if request.count > 1:
            body["n"] = request.count
        if "seed" in model.parameters:
            body["seed"] = request.seed
        if request.reference_urls:
            body["input_references"] = [
                {"type": "image_url", "image_url": {"url": url}} for url in request.reference_urls
            ]
        document = await post_json(IMAGES_URL, apply_options(body, request.options, "images"), configuration)
        try:
            reply = ImageReply.model_validate(document)
            files = [(base64.b64decode(item.b64_json, validate=True), item.media_type) for item in reply.images]
        except (ValidationError, binascii.Error):
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if not files:
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_EMPTY)
        return ImageResult(
            tuple(
                ImageOutput(content, SVG_MEDIA_TYPE if content.lstrip().startswith(SVG_STARTS) else media or "")
                for content, media in files
            )
        )


__all__ = ["ImageOperation"]

"""Send one request to OpenRouter's image endpoint and read the files it returns."""

from __future__ import annotations

import base64
import binascii
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
from ..config.generation.images import COMPRESSED_FORMATS
from ..config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ..config.messages.inputs import PROMPT_EMPTY, REFERENCES_RANGE, IMAGE_COUNT_RANGE, TRANSPARENT_FORMAT

if TYPE_CHECKING:
    from ..state import Json
    from ..state.images import ImageRequest
    from ..state.settings import Settings, ExecutionConfiguration


class ImageOperation:
    """One image request, refused before sending when the model cannot take it.

    A failed image request is not billed: the endpoint bills only completed images.
    """

    def __init__(self, request: ImageRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty prompt, counts outside the model's ranges, and a transparent JPEG."""
        request = self.request
        if not request.prompt.strip():
            raise ConnectorError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        if request.fields.get("background") == "transparent" and request.fields.get("output_format") == "jpeg":
            raise ConnectorError(ErrorCode.INVALID_INPUT, TRANSPARENT_FORMAT)
        check_upload_size(request.reference_urls, settings)
        choice = request.choice
        if choice is None:
            return
        count = choice.parameters.get("n")
        if count is not None and not (count.minimum or 1) <= request.count <= (count.maximum or request.count):
            message = IMAGE_COUNT_RANGE.format(minimum=count.minimum, maximum=count.maximum)
            raise ConnectorError(ErrorCode.INVALID_INPUT, message)
        references = choice.parameters.get("input_references")
        low = references.minimum or 0 if references else 0
        high = references.maximum or 0 if references else 0
        if not low <= len(request.reference_urls) <= high:
            message = REFERENCES_RANGE.format(minimum=low, maximum=high, count=len(request.reference_urls))
            raise ConnectorError(ErrorCode.INVALID_INPUT, message)

    async def send(self, configuration: ExecutionConfiguration) -> ImageResult:
        """Send the request and read every image; an SVG file is recognized by its type or its first bytes."""
        request, choice = self.request, self.request.choice
        body: dict[str, Json] = {"model": request.model_id, "prompt": request.prompt}
        if choice is None or "n" in choice.parameters:
            body["n"] = request.count
        if choice is None or "seed" in choice.parameters:
            body["seed"] = request.seed
        fields = dict(request.fields)
        if fields.get("output_format") not in COMPRESSED_FORMATS:
            fields.pop("output_compression", None)
        body.update(fields)
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

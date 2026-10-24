"""Send one request to OpenRouter's image endpoint and read the files it returns."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING
import binascii
from dataclasses import dataclass

from pydantic import ValidationError

from .models import validate_model, validate_limits, read_image_limits
from .options import build_request_body
from .operation import validate_upload_size
from .transport import send_json
from ..config.media import SVG_STARTS, SVG_MEDIA_TYPE
from ..state.errors import ErrorCode, OpenRouterError
from ..state.images import ImageOutput, ImageResult
from ..state.replies import ImageReply
from ..config.openrouter import ENDPOINT_URLS
from ..config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE
from ..config.messages.inputs import SIZE_PAIR, SIZE_SHAPE, PROMPT_EMPTY, TRANSPARENT_FORMAT
from ..config.messages.models import MODEL_COUNT

if TYPE_CHECKING:
    from ..state import Json
    from ..state.images import ImageRequest
    from ..state.models import Limits
    from ..state.settings import Settings, Configuration


@dataclass(frozen=True, slots=True)
class ImageOperation:
    """One image request; a failed one is not billed, because the endpoint bills only completed images.

    Attributes:
        request: The request to validate and send.

    """

    request: ImageRequest

    def validate(self, settings: Settings) -> None:
        """Refuse an empty prompt, a lone width or height, a size with a shape, a transparent JPEG, and too much media.

        OpenRouter refuses an exact size sent with a resolution or an aspect ratio, because the size sets both.
        """
        request = self.request
        if not request.prompt.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        if (request.width == 0) != (request.height == 0):
            raise OpenRouterError(ErrorCode.INVALID_INPUT, SIZE_PAIR)
        if request.width and not {'resolution', 'aspect_ratio'}.isdisjoint(request.fields):
            raise OpenRouterError(ErrorCode.INVALID_INPUT, SIZE_SHAPE)
        if request.fields.get('background') == 'transparent' and request.fields.get('output_format') == 'jpeg':
            raise OpenRouterError(ErrorCode.INVALID_INPUT, TRANSPARENT_FORMAT)
        validate_upload_size(request.reference_urls, settings)

    def build_fields(self, limits: Limits | None) -> dict[str, Json]:
        """Check the fields, n, and references against the model's image listing when it has one.

        The request leaves out the compression, which always has a value, for a model that does not take it. The
        exact size goes unchecked, because the listings do not list it.
        """
        request = self.request
        fields: dict[str, Json] = dict(request.fields)
        if request.n > 1:
            fields['n'] = request.n
        if request.width:
            fields['size'] = f'{request.width}x{request.height}'
        if limits is None:
            return fields
        if 'output_compression' not in limits.fields:
            fields.pop('output_compression', None)
        # A model that does not list n makes one image per request.
        maximum = int(limits.ranges['n'][1]) if 'n' in limits.ranges else 1
        if request.n > maximum:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_COUNT.format(model=request.model_id, maximum=maximum))
        checked = {field: value for field, value in fields.items() if field not in {'n', 'size'}}
        if request.reference_urls or 'input_references' in limits.fields:
            checked['input_references'] = len(request.reference_urls)
        validate_limits(request.model_id, limits, checked)
        return fields

    async def send(self, configuration: Configuration) -> ImageResult:
        """Check the model, send, and read every image; the type or the first bytes identify an SVG file."""
        request = self.request
        inputs = ['image'] if request.reference_urls else []
        model = await validate_model(request.model_id, 'images', configuration.settings, inputs)
        limits = await read_image_limits(request.model_id, configuration.settings)
        body: dict[str, Json] = {'model': request.model_id, 'prompt': request.prompt, **self.build_fields(limits)}
        if 'seed' in (limits.fields if limits is not None else model.parameters):
            body['seed'] = request.seed
        if request.reference_urls:
            body['input_references'] = [
                {'type': 'image_url', 'image_url': {'url': url}} for url in request.reference_urls
            ]
        document = await send_json(
            ENDPOINT_URLS['images'], build_request_body(body, request.options, 'images'), configuration
        )
        try:
            reply = ImageReply.model_validate(document)
            files = [(base64.b64decode(item.encoded, validate=True), item.media_type) for item in reply.images]
        except (ValidationError, binascii.Error):
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if not files:
            raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_EMPTY)
        return ImageResult(
            tuple(
                ImageOutput(content, SVG_MEDIA_TYPE if content.lstrip().startswith(SVG_STARTS) else media or '')
                for content, media in files
            )
        )


__all__ = ['ImageOperation']

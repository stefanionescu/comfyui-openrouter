"""Send one chat completion and read its text, reasoning, images, and audio."""

from __future__ import annotations

from http import HTTPStatus
import base64
from typing import TYPE_CHECKING
import binascii
from dataclasses import dataclass

from .audio import send_audio_chat
from ..models import validate_model
from .content import build_body
from ..failures import read_failure, sanitize_reason
from ..operation import validate_upload_size
from ..transport import send_json, read_reply, download_media
from ...state.chat import ChatResult
from ...state.errors import ErrorCode, OpenRouterError
from ...state.replies import ChatReply, ErrorReply, ChatMessage
from ...config.openrouter import MEDIA_LABELS, ENDPOINT_URLS, SCHEMA_PARAMETERS
from ...config.messages.run import ANSWER_CUT, REPLY_EMPTY, MODEL_REFUSED, ANSWER_FILTERED, REPLY_UNREADABLE
from ...config.messages.inputs import PROMPT_EMPTY
from ...config.messages.models import MODEL_FIELD, MODEL_OUTPUT, MODEL_SCHEMA, MODEL_TOKENS

if TYPE_CHECKING:
    from ...state import Json
    from ...state.chat import ChatRequest
    from ...state.models import Model
    from ...state.settings import Settings, Configuration


@dataclass(frozen=True, slots=True)
class ChatOperation:
    """One chat completion.

    Attributes:
        request: The request to validate and send.

    """

    request: ChatRequest

    def validate(self, settings: Settings) -> None:
        """Refuse an empty prompt and media over the upload limit."""
        request = self.request
        if not request.prompt.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        documents = (document.file_url or '' for document in request.documents)
        validate_upload_size((*request.image_urls, *request.video_urls, *request.audio_clips, *documents), settings)

    async def send(self, configuration: Configuration) -> ChatResult:
        """Check the model, then send; an answer cut at the output token limit comes back as it is."""
        request = self.request
        media = {'image': request.image_urls, 'video': request.video_urls, 'audio': request.audio_clips}
        inputs = [kind for kind, items in media.items() if items]
        model = await validate_model(request.model_id, 'chat', configuration.settings, inputs)
        _validate_settings(request, model)
        body = build_body(request, model)
        if 'audio' in request.settings.outputs:
            result = await send_audio_chat(body, configuration)
            if not result.text and result.audio is None:
                raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_EMPTY)
            return result
        message, finish_reason = _read_message(await send_json(ENDPOINT_URLS['chat'], body, configuration))
        if isinstance(message.content, list):
            parts = (part for part in message.content if isinstance(part, dict))
            text = ''.join(str(part.get('text', '')) for part in parts if part.get('type') == 'text')
        else:
            text = message.content or ''
        images = tuple([await _read_image(item.image_url.url, configuration.settings) for item in message.images])
        images = tuple(image for image in images if image)
        if not text and not images:
            ended = {'length': ANSWER_CUT, 'content_filter': ANSWER_FILTERED}.get(finish_reason or '', REPLY_EMPTY)
            raise OpenRouterError(ErrorCode.TRANSPORT, ended)
        return ChatResult(text=text, reasoning=message.reasoning or '', images=images, audio=None, is_pcm=False)


def _validate_settings(request: ChatRequest, model: Model) -> None:
    """Refuse outputs the model cannot make, a field or schema it does not take, and more tokens than it gives."""
    settings = request.settings
    missing = sorted(settings.outputs - model.outputs)
    if missing:
        message = MODEL_OUTPUT.format(model=request.model_id, kind=MEDIA_LABELS[missing[0]])
        raise OpenRouterError(ErrorCode.INVALID_INPUT, message)
    fields = (*settings.sampling, *(('stop',) if settings.stop else ()))
    unknown = next((field for field in fields if field not in model.parameters), None)
    if unknown is not None:
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_FIELD.format(model=request.model_id, field=unknown))
    if settings.json_schema is not None and model.parameters.isdisjoint(SCHEMA_PARAMETERS):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_SCHEMA.format(model=request.model_id))
    if model.max_completion_tokens is not None and settings.max_tokens > model.max_completion_tokens:
        message = MODEL_TOKENS.format(model=request.model_id, maximum=model.max_completion_tokens)
        raise OpenRouterError(ErrorCode.INVALID_INPUT, message)


def _read_message(document: Json) -> tuple[ChatMessage, str | None]:
    """Read the first choice's message and why it ended, refusing a failed choice and a model's refusal."""
    reply = read_reply(ChatReply, document)
    if not reply.choices:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    choice = reply.choices[0]
    if choice.error is not None:
        status = choice.error.code if isinstance(choice.error.code, int) else HTTPStatus.BAD_GATEWAY
        raise read_failure(status, ErrorReply(error=choice.error).model_dump_json().encode())
    message = choice.message or ChatMessage()
    if message.refusal:
        reason = sanitize_reason(message.refusal)
        raise OpenRouterError(ErrorCode.REFUSED, MODEL_REFUSED.format(reason=reason))
    return message, choice.finish_reason


async def _read_image(url: str, settings: Settings) -> bytes:
    """Read an image a chat model made: a data URL, or an address on a provider's host read without the key."""
    if url.startswith('https://'):
        return await download_media(url, settings)
    if not url.startswith('data:') or ',' not in url:
        return b''
    try:
        return base64.b64decode(url.split(',', 1)[1], validate=True)
    except binascii.Error:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


__all__ = ['ChatOperation']

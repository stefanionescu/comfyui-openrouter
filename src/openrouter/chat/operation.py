"""Send one chat completion and read its text, reasoning, images, and audio."""

from __future__ import annotations

import base64
import binascii
from http import HTTPStatus
from .content import build_body
from typing import TYPE_CHECKING
from .audio import send_audio_chat
from ..models import validate_model
from ...types.chat import ChatResult
from pydantic import ValidationError
from ..operation import validate_upload_size
from ..transport import send_json, download_media
from ...config.messages.inputs import PROMPT_EMPTY
from ..failures import sanitize_reason, read_failure
from ...types.errors import ErrorCode, OpenRouterError
from ...types.replies import ChatReply, ErrorReply, ChatMessage
from ...config.messages.models import MODEL_OUTPUT, MODEL_SCHEMA, MODEL_TOKENS
from ...config.openrouter import ENDPOINT_URLS, MEDIA_LABELS, SCHEMA_PARAMETERS
from ...config.messages.run import ANSWER_CUT, REPLY_EMPTY, MODEL_REFUSED, ANSWER_FILTERED, REPLY_UNREADABLE

if TYPE_CHECKING:
    from ...types import Json
    from ...types.models import Model
    from ...types.chat import ChatRequest
    from ...types.settings import Settings, Configuration


class ChatOperation:
    """One chat completion."""

    def __init__(self, request: ChatRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty prompt and media over the upload limit."""
        request = self.request
        if not request.prompt.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        documents = (document.file_url or "" for document in request.documents)
        validate_upload_size((*request.image_urls, *request.video_urls, *request.audio_clips, *documents), settings)

    async def send(self, configuration: Configuration) -> ChatResult:
        """Check the model, then send; an answer cut at the output token limit is returned as it is."""
        request = self.request
        media = {"image": request.image_urls, "video": request.video_urls, "audio": request.audio_clips}
        inputs = [kind for kind, items in media.items() if items]
        model = await validate_model(request.model_id, "chat", configuration.settings, inputs)
        _validate_settings(request, model)
        body = build_body(request, model.parameters)
        if "audio" in request.settings.outputs:
            result = await send_audio_chat(body, configuration)
            if not result.text and result.audio is None:
                raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_EMPTY)
            return result
        message, finish_reason = _read_message(await send_json(ENDPOINT_URLS["chat"], body, configuration))
        if isinstance(message.content, list):
            parts = (part for part in message.content if isinstance(part, dict))
            text = "".join(str(part.get("text", "")) for part in parts if part.get("type") == "text")
        else:
            text = message.content or ""
        images = tuple([await _read_image(item.image_url.url, configuration.settings) for item in message.images])
        images = tuple(image for image in images if image)
        if not text and not images:
            ended = {"length": ANSWER_CUT, "content_filter": ANSWER_FILTERED}.get(finish_reason or "", REPLY_EMPTY)
            raise OpenRouterError(ErrorCode.TRANSPORT, ended)
        return ChatResult(text=text, reasoning=message.reasoning or "", images=images, audio=None, is_pcm=False)


def _validate_settings(request: ChatRequest, model: Model) -> None:
    """Refuse outputs the model cannot make, a schema it cannot follow, and more tokens than any provider gives."""
    settings = request.settings
    missing = sorted(settings.outputs - model.outputs)
    if missing:
        message = MODEL_OUTPUT.format(model=request.model_id, kind=MEDIA_LABELS[missing[0]])
        raise OpenRouterError(ErrorCode.INVALID_INPUT, message)
    if settings.answer_schema is not None and model.parameters.isdisjoint(SCHEMA_PARAMETERS):
        raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_SCHEMA.format(model=request.model_id))
    if model.max_completion_tokens is not None and settings.max_tokens > model.max_completion_tokens:
        message = MODEL_TOKENS.format(model=request.model_id, maximum=model.max_completion_tokens)
        raise OpenRouterError(ErrorCode.INVALID_INPUT, message)


def _read_message(document: Json) -> tuple[ChatMessage, str | None]:
    """Read the first choice's message and why it ended, refusing a failed choice and a model's refusal."""
    try:
        reply = ChatReply.model_validate(document)
    except ValidationError:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
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
    if url.startswith("https://"):
        return await download_media(url, settings)
    if not url.startswith("data:") or "," not in url:
        return b""
    try:
        return base64.b64decode(url.split(",", 1)[1], validate=True)
    except binascii.Error:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


__all__ = ["ChatOperation"]

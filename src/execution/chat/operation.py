"""Send one chat completion and read its text, reasoning, images, and audio."""

from __future__ import annotations

import base64
import binascii
from .audio import stream_audio
from .content import build_body
from typing import TYPE_CHECKING
from ...state.chat import ChatResult
from pydantic import ValidationError
from ...config.openrouter import CHAT_URL
from ..operation import check_upload_size
from ...errors import ErrorCode, ConnectorError
from ..failures import clean_reason, read_failure
from ..transport import post_json, download_public
from ...state.replies import ChatReply, ErrorReply, ChatMessage
from ...config.messages.run import REPLY_EMPTY, MODEL_REFUSED, REPLY_UNREADABLE
from ...config.generation.chat import MAX_PROMPT_CHARACTERS, MAX_CONVERSATION_TURNS
from ...config.messages.inputs import (
    PROMPT_EMPTY,
    PROMPT_LENGTH,
    CONVERSATION_LIMIT,
    INPUT_NOT_ACCEPTED,
    OUTPUT_TOKENS_RANGE,
)

if TYPE_CHECKING:
    from ...state import Json
    from ...state.chat import ChatRequest
    from ...state.settings import Settings, ExecutionConfiguration


class ChatOperation:
    """One chat completion, refused before sending when the model cannot take its inputs."""

    def __init__(self, request: ChatRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse an empty or oversized prompt, a long conversation, too much media, and inputs the model lacks.

        The dropdown shows only sockets a model accepts, so these checks matter for a written ID the saved
        list holds and for inputs connected before switching models.
        """
        request = self.request
        if not request.prompt.strip():
            raise ConnectorError(ErrorCode.INVALID_INPUT, PROMPT_EMPTY)
        if len(request.prompt) > MAX_PROMPT_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, PROMPT_LENGTH.format(maximum=MAX_PROMPT_CHARACTERS))
        if len(request.conversation.turns) > MAX_CONVERSATION_TURNS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, CONVERSATION_LIMIT.format(maximum=MAX_CONVERSATION_TURNS))
        documents = (document.file_url or "" for document in request.documents)
        check_upload_size((*request.image_urls, *request.video_urls, *request.audio_clips, *documents), settings)
        choice = request.choice
        if choice is None:
            return
        for kind, media in (
            ("image", request.image_urls),
            ("video", request.video_urls),
            ("audio", request.audio_clips),
        ):
            if media and kind not in choice.inputs:
                raise ConnectorError(ErrorCode.INVALID_INPUT, INPUT_NOT_ACCEPTED.format(model=choice.name, kind=kind))
        maximum = choice.max_output_tokens
        if maximum is not None and request.settings.max_output_tokens > maximum:
            raise ConnectorError(ErrorCode.INVALID_INPUT, OUTPUT_TOKENS_RANGE.format(maximum=maximum))

    async def send(self, configuration: ExecutionConfiguration) -> ChatResult:
        """Send the completion; an answer cut at the output token limit is returned as it is."""
        body = build_body(self.request)
        if "audio" in self.request.settings.outputs:
            return await stream_audio(body, configuration)
        message = _read_message(await post_json(CHAT_URL, body, configuration))
        if isinstance(message.content, list):
            parts = (part for part in message.content if isinstance(part, dict))
            text = "".join(str(part.get("text", "")) for part in parts if part.get("type") == "text")
        else:
            text = message.content or ""
        images = tuple([await _read_image(item.image_url.url, configuration) for item in message.images])
        images = tuple(image for image in images if image)
        if not text and not images:
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_EMPTY)
        return ChatResult(text=text, reasoning=message.reasoning or "", images=images, audio=None, is_pcm=False)


def _read_message(document: Json) -> ChatMessage:
    """Read the first choice's message, refusing a failed choice and a model's refusal."""
    try:
        reply = ChatReply.model_validate(document)
    except ValidationError:
        raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    if not reply.choices:
        raise ConnectorError(ErrorCode.TRANSPORT, REPLY_EMPTY)
    choice = reply.choices[0]
    if choice.error is not None:
        status = choice.error.code if isinstance(choice.error.code, int) else 502
        raise read_failure(status, ErrorReply(error=choice.error).model_dump_json().encode())
    message = choice.message or ChatMessage()
    if message.refusal:
        reason = clean_reason(message.refusal)
        raise ConnectorError(ErrorCode.REFUSED, MODEL_REFUSED.format(reason=reason))
    return message


async def _read_image(url: str, configuration: ExecutionConfiguration) -> bytes:
    """Read an image a chat model made: a data URL, or an address on a provider's host read without the key."""
    if url.startswith("https://"):
        return await download_public(url, configuration)
    if not url.startswith("data:") or "," not in url:
        return b""
    try:
        return base64.b64decode(url.split(",", 1)[1], validate=True)
    except binascii.Error:
        raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None


__all__ = ["ChatOperation"]

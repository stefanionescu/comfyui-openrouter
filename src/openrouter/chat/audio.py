"""Collect the streamed reply of a chat model that answers with audio."""

from __future__ import annotations

import base64
import binascii
from ..transport import send_stream
from ...types.chat import ChatResult
from typing import cast, TYPE_CHECKING
from ...config.openrouter import CHAT_URL
from ...config.messages.run import REPLY_UNREADABLE
from ...types.errors import ErrorCode, OpenRouterError

if TYPE_CHECKING:
    from ...types import Json
    from collections.abc import Mapping
    from ...types.settings import Configuration


async def send_audio_chat(body: Mapping[str, Json], configuration: Configuration) -> ChatResult:
    """Join the streamed text, audio chunks, and spoken words into one result.

    Voice models answer in raw PCM, and music models in an encoded file. Raw PCM has no header to
    recognize, so the request decides the format: only a voice request carries an audio object.
    """
    text: list[str] = []
    chunks: list[str] = []
    transcript: list[str] = []
    async for event in send_stream(CHAT_URL, body, configuration):
        choices = cast("dict[str, Json]", event).get("choices") if isinstance(event, dict) else None
        delta = cast("dict[str, Json]", choices[0]).get("delta") if isinstance(choices, list) and choices else None
        if not isinstance(delta, dict):
            continue
        if isinstance(content := delta.get("content"), str):
            text.append(content)
        audio = delta.get("audio")
        if isinstance(audio, dict):
            if isinstance(chunk := audio.get("data"), str):
                chunks.append(chunk)
            if isinstance(words := audio.get("transcript"), str):
                transcript.append(words)
    try:
        content = base64.b64decode("".join(chunks), validate=True) if chunks else None
    except binascii.Error:
        raise OpenRouterError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
    # The spoken words arrive only as the transcript, so they stand in for empty text.
    answer = "".join(text) or "".join(transcript)
    return ChatResult(text=answer, reasoning="", images=(), audio=content, is_pcm="audio" in body)


__all__ = ["send_audio_chat"]

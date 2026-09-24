"""Send one transcription request and turn its segments into subtitles and its words into timed words."""

from __future__ import annotations

import re
from .transport import post_json
from typing import TYPE_CHECKING
from .options import apply_options
from pydantic import ValidationError
from .operation import check_upload_size
from ..config.patterns import LANGUAGE_PATTERN
from ..errors import ErrorCode, ConnectorError
from ..state.replies import TranscriptionReply
from ..config.openrouter import TRANSCRIPTION_URL
from ..config.messages.inputs import LANGUAGE_CODE
from ..state.audio import Segment, TranscriptionResult
from ..config.messages.run import REPLY_EMPTY, REPLY_UNREADABLE

if TYPE_CHECKING:
    from ..state import Json
    from collections.abc import Sequence
    from ..state.audio import TranscriptionRequest
    from ..state.settings import Settings, ExecutionConfiguration

LANGUAGE = re.compile(LANGUAGE_PATTERN)
GRANULARITIES = {"segments": ["segment"], "words and segments": ["segment", "word"]}


def format_subtitles(segments: Sequence[Segment]) -> str:
    """Write the segments as SRT subtitles, with the speaker in square brackets when known."""
    blocks: list[str] = []
    for number, segment in enumerate(segments, 1):
        times: list[str] = []
        for seconds in (segment.start, segment.end):
            minutes, milliseconds = divmod(round(seconds * 1000), 60_000)
            hours, minutes = divmod(minutes, 60)
            times.append(f"{hours:02}:{minutes:02}:{milliseconds // 1000:02},{milliseconds % 1000:03}")
        text = f"[{segment.speaker}] {segment.text}" if segment.speaker else segment.text
        blocks.append(f"{number}\n{times[0]} --> {times[1]}\n{text}\n")
    return "\n".join(blocks)


class TranscriptionOperation:
    """One transcription request, refused before sending when its language code or clip is out of bounds."""

    def __init__(self, request: TranscriptionRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse a clip above the upload limit and a language that is not a two-letter code."""
        check_upload_size((self.request.clip,), settings)
        language = self.request.language
        if language and LANGUAGE.match(language) is None:
            raise ConnectorError(ErrorCode.INVALID_INPUT, LANGUAGE_CODE)

    async def send(self, configuration: ExecutionConfiguration) -> TranscriptionResult:
        """Send the clip; Whisper starts its text and segments with a space, so every text is stripped."""
        request = self.request
        body: dict[str, Json] = {"model": request.model_id, "input_audio": {"data": request.clip, "format": "wav"}}
        if request.language:
            body["language"] = request.language
        if request.temperature > 0:
            body["temperature"] = request.temperature
        if request.timestamps in GRANULARITIES:
            body["response_format"] = "verbose_json"
            body["timestamp_granularities"] = list(GRANULARITIES[request.timestamps])
        document = await post_json(
            TRANSCRIPTION_URL, apply_options(body, request.options, "transcription"), configuration
        )
        try:
            reply = TranscriptionReply.model_validate(document)
        except ValidationError:
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_UNREADABLE) from None
        if not reply.text.strip():
            raise ConnectorError(ErrorCode.TRANSPORT, REPLY_EMPTY)
        segments = tuple(
            Segment(item.start or 0.0, item.end or 0.0, item.text.strip(), item.speaker) for item in reply.segments
        )
        words = tuple(Segment(item.start or 0.0, item.end or 0.0, item.word.strip(), None) for item in reply.words)
        return TranscriptionResult(reply.text.strip(), segments, words)


__all__ = ["TranscriptionOperation", "format_subtitles"]

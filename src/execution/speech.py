"""Send one text-to-speech request and read the audio's format from the reply."""

from __future__ import annotations

from typing import TYPE_CHECKING
from .transport import post_audio
from .options import apply_options
from .operation import check_upload_size
from ..config.openrouter import SPEECH_URL
from ..errors import ErrorCode, ConnectorError
from ..state.audio import PcmFormat, SpeechResult
from ..config.messages.inputs import PCM_RATE_MISSING, SPEECH_TEXT_EMPTY, VOICE_SAMPLE_SIZE, SPEECH_TEXT_LENGTH
from ..config.generation.audio import DEFAULT_SPEED, PCM_MEDIA_TYPE, MAX_SPEECH_CHARACTERS, MAX_VOICE_SAMPLE_BYTES

if TYPE_CHECKING:
    from ..state import Json
    from ..state.audio import SpeechRequest
    from ..state.settings import Settings, ExecutionConfiguration


def read_pcm_format(media_type: str) -> PcmFormat | None:
    """Read the rate and channels of raw PCM from the reply's Content-Type, or None for an encoded file.

    The reply decides the format, not the request, because a provider can answer a PCM request with MP3.
    """
    kind, *parameters = (part.strip() for part in media_type.split(";"))
    if kind.lower() != PCM_MEDIA_TYPE:
        return None
    values: dict[str, str] = {}
    for parameter in parameters:
        name, _separator, value = parameter.partition("=")
        values[name.strip().lower()] = value.strip()
    rate, channels = values.get("rate", ""), values.get("channels", "")
    if not rate.isdigit() or not channels.isdigit() or int(rate) == 0 or int(channels) == 0:
        raise ConnectorError(ErrorCode.TRANSPORT, PCM_RATE_MISSING)
    return PcmFormat(int(rate), int(channels))


class SpeechOperation:
    """One speech request, refused before sending when its text or sample is out of bounds."""

    def __init__(self, request: SpeechRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse empty or overlong text and an oversized voice sample."""
        request = self.request
        if not request.text.strip():
            raise ConnectorError(ErrorCode.INVALID_INPUT, SPEECH_TEXT_EMPTY)
        if len(request.text) > MAX_SPEECH_CHARACTERS:
            raise ConnectorError(ErrorCode.INVALID_INPUT, SPEECH_TEXT_LENGTH.format(maximum=MAX_SPEECH_CHARACTERS))
        sample = request.sample or ""
        if len(sample.partition(",")[2]) * 3 // 4 > MAX_VOICE_SAMPLE_BYTES:
            raise ConnectorError(ErrorCode.INVALID_INPUT, VOICE_SAMPLE_SIZE)
        check_upload_size((sample,), settings)

    async def send(self, configuration: ExecutionConfiguration) -> SpeechResult:
        """Send the text, the voice when chosen, and the sample when connected, and keep the reply's format."""
        request = self.request
        body: dict[str, Json] = {
            "model": request.model_id,
            "input": request.text,
            "response_format": request.audio_format,
        }
        if request.voice:
            body["voice"] = request.voice
        if request.speed != DEFAULT_SPEED:
            body["speed"] = request.speed
        if request.sample:
            references: list[Json] = [{"type": "input_audio", "input_audio": {"data": request.sample}}]
            if request.sample_transcript.strip():
                references.append({"type": "text", "text": request.sample_transcript})
            body["input_references"] = references
        audio = await post_audio(SPEECH_URL, apply_options(body, request.options, "speech"), configuration)
        return SpeechResult(audio, read_pcm_format(audio.media_type))


__all__ = ["SpeechOperation", "read_pcm_format"]

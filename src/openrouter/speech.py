"""Send one text-to-speech request and read the audio's format from the reply."""

from __future__ import annotations

from typing import TYPE_CHECKING
from .models import validate_model
from .transport import send_speech
from .options import build_request_body
from ..config.media import PCM_MEDIA_TYPE
from ..config.generation.audio import SPEED
from .operation import validate_upload_size
from ..config.openrouter import ENDPOINT_URLS
from ..config.messages.models import MODEL_VOICE
from ..types.audio import PcmFormat, SpeechResult
from ..types.errors import ErrorCode, OpenRouterError
from ..config.messages.inputs import PCM_RATE_MISSING, SPEECH_TEXT_EMPTY

if TYPE_CHECKING:
    from ..types import Json
    from ..types.audio import SpeechRequest
    from ..types.settings import Settings, Configuration


def _read_pcm_format(media_type: str) -> PcmFormat | None:
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
        raise OpenRouterError(ErrorCode.TRANSPORT, PCM_RATE_MISSING)
    return PcmFormat(int(rate), int(channels))


class SpeechOperation:
    """One speech request, refused before sending when its text or sample is out of bounds."""

    def __init__(self, request: SpeechRequest) -> None:
        """Keep the request to validate and send."""
        self.request = request

    def validate(self, settings: Settings) -> None:
        """Refuse empty text and a voice sample over the upload limit."""
        request = self.request
        if not request.text.strip():
            raise OpenRouterError(ErrorCode.INVALID_INPUT, SPEECH_TEXT_EMPTY)
        validate_upload_size((request.sample or "",), settings)

    async def send(self, configuration: Configuration) -> SpeechResult:
        """Check the model, send the text with the voice and sample when set, and keep the reply's format.

        A voice sample needs a model with a provider that clones voices.
        """
        request = self.request
        model = await validate_model(request.model_id, "speech", configuration.settings)
        if request.sample and not model.has_voice_cloning:
            raise OpenRouterError(ErrorCode.INVALID_INPUT, MODEL_VOICE.format(model=request.model_id))
        body: dict[str, Json] = {
            "model": request.model_id,
            "input": request.text,
            "response_format": request.audio_format,
        }
        if request.voice:
            body["voice"] = request.voice
        if request.speed != SPEED["DEFAULT"]:
            body["speed"] = request.speed
        if request.sample:
            references: list[Json] = [{"type": "input_audio", "input_audio": {"data": request.sample}}]
            if request.sample_transcript.strip():
                references.append({"type": "text", "text": request.sample_transcript})
            body["input_references"] = references
        audio = await send_speech(
            ENDPOINT_URLS["speech"], build_request_body(body, request.options, "speech"), configuration
        )
        return SpeechResult(audio, _read_pcm_format(audio.media_type))


__all__ = ["SpeechOperation"]

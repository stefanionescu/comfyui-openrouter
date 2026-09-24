"""Audio replies, speech and transcription requests, and their results."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import Options


@dataclass(frozen=True, slots=True)
class AudioReply:
    """A raw audio body OpenRouter sent, with its media type.

    Attributes:
        content: The audio bytes.
        media_type: The reply's Content-Type, with its parameters.

    """

    content: bytes
    media_type: str


@dataclass(frozen=True, slots=True)
class PcmFormat:
    """The shape of raw PCM, which has no header of its own.

    Attributes:
        sample_rate: Samples per second.
        channels: Number of channels.

    """

    sample_rate: int
    channels: int


@dataclass(frozen=True, slots=True)
class SpeechRequest:
    """One text-to-speech request.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        text: What to say.
        voice: The voice, or None for the provider's default voice.
        audio_format: pcm or mp3, the format OpenRouter sends.
        speed: Speaking speed; some providers ignore it.
        sample: A voice sample to copy, as a data:audio/wav URI, or None.
        sample_transcript: What the sample says, or empty.
        options: Provider routing and extra fields.

    """

    model_id: str
    text: str
    voice: str | None
    audio_format: str
    speed: float
    sample: str | None
    sample_transcript: str
    options: Options | None


@dataclass(frozen=True, slots=True)
class SpeechResult:
    """The audio a speech model made.

    Attributes:
        audio: The reply body and its media type.
        pcm: The PCM shape when the reply is raw PCM, or None for an encoded file such as MP3.

    """

    audio: AudioReply
    pcm: PcmFormat | None


@dataclass(frozen=True, slots=True)
class TranscriptionRequest:
    """One transcription request.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        clip: Base64 WAV without a data: prefix, as the endpoint takes it.
        language: Two-letter language code, or empty.
        timestamps: none, segments, or words and segments.
        temperature: Sampling temperature; 0 sends none.
        options: Provider options.

    """

    model_id: str
    clip: str
    language: str
    timestamps: str
    temperature: float
    options: Options | None


@dataclass(frozen=True, slots=True)
class Segment:
    """One timed part of a transcript.

    Attributes:
        start: Start in seconds.
        end: End in seconds.
        text: What was said.
        speaker: Who said it, when the model tells speakers apart.

    """

    start: float
    end: float
    text: str
    speaker: str | None


@dataclass(frozen=True, slots=True)
class TranscriptionResult:
    """A transcript, its timed segments, and its timed words.

    Attributes:
        text: The whole transcript.
        segments: Timed parts, empty without timestamps.
        words: Timed words, with no speaker; empty unless word timestamps were requested.

    """

    text: str
    segments: tuple[Segment, ...]
    words: tuple[Segment, ...]


__all__ = [
    "AudioReply",
    "PcmFormat",
    "Segment",
    "SpeechRequest",
    "SpeechResult",
    "TranscriptionRequest",
    "TranscriptionResult",
]

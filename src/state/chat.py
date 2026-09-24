"""Chat documents, conversations, requests, and results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Json
    from .options import RequestOptions
    from collections.abc import Mapping


@dataclass(frozen=True, slots=True)
class Document:
    """One file attached to a chat request.

    Attributes:
        name: The file name the model sees.
        media_type: The file's media type.
        text: The contents of a text file.
        file_url: A PDF as a data URL.

    """

    name: str
    media_type: str
    text: str | None
    file_url: str | None


@dataclass(frozen=True, slots=True)
class Turn:
    """One message of an earlier exchange.

    Attributes:
        role: Who wrote the message.
        text: What the message says.

    """

    role: Literal["user", "assistant"]
    text: str


@dataclass(frozen=True, slots=True)
class Conversation:
    """The turns before the next question, oldest first.

    Attributes:
        turns: The earlier messages.

    """

    turns: tuple[Turn, ...]


@dataclass(frozen=True, slots=True)
class ChatSettings:
    """The per-model chat controls.

    Attributes:
        effort: Reasoning effort, or None for the model's default.
        max_output_tokens: Largest answer in tokens, or 0 for the model's default.
        temperature: Sampling temperature, sent when the model takes one.
        answer_schema: JSON schema the answer must follow, or None for free text.
        outputs: Media to make besides text: image, audio.
        aspect_ratio: Aspect ratio of generated images, or None for the model's default.
        voice: Voice of spoken replies, or None when the voice box is blank.
        pdf_engine: How OpenRouter reads PDFs, or None for the model's default.

    """

    effort: str | None
    max_output_tokens: int
    temperature: float
    answer_schema: Mapping[str, Json] | None
    outputs: frozenset[str]
    aspect_ratio: str | None
    voice: str | None
    pdf_engine: str | None


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """One chat completion with its media already encoded.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        system: System instructions, sent when not blank.
        prompt: The question.
        conversation: Earlier turns sent before the question.
        image_urls: PNG data URLs.
        video_urls: MP4 data URLs.
        audio_clips: Base64 WAV without a data: prefix, as the input_audio part takes it.
        documents: Attached files.
        seed: Seed sent when the model accepts one.
        settings: The per-model controls.
        options: Provider routing and extra fields.

    """

    model_id: str
    system: str
    prompt: str
    conversation: Conversation
    image_urls: tuple[str, ...]
    video_urls: tuple[str, ...]
    audio_clips: tuple[str, ...]
    documents: tuple[Document, ...]
    seed: int
    settings: ChatSettings
    options: RequestOptions | None


@dataclass(frozen=True, slots=True)
class ChatResult:
    """What one chat completion returned.

    Attributes:
        text: The answer, or the spoken words of an audio answer.
        reasoning: The model's reasoning text, when it shares it.
        images: Encoded images the model made.
        audio: Audio the model made, or None.
        is_pcm: Whether the audio is raw 16-bit PCM rather than an encoded file.

    """

    text: str
    reasoning: str
    images: tuple[bytes, ...]
    audio: bytes | None
    is_pcm: bool


__all__ = ["ChatRequest", "ChatResult", "ChatSettings", "Conversation", "Document", "Turn"]

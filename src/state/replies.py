"""The parts of OpenRouter's replies the extension reads; unknown fields are ignored."""

from . import Json, Reply
from pydantic import Field
from collections.abc import Mapping


class ErrorMetadata(Reply):
    """Where a provider's own reason sits when OpenRouter only says the provider returned an error."""

    raw: str | None = None


class ErrorBody(Reply):
    """One OpenRouter error."""

    code: int | str | None = None
    message: str = ""
    metadata: ErrorMetadata | None = None


class ErrorReply(Reply):
    """An OpenRouter error document."""

    error: ErrorBody


class ImageUrl(Reply):
    """The address of one image a chat model made."""

    url: str


class ChatImage(Reply):
    """One image a chat model made."""

    image_url: ImageUrl


class ChatMessage(Reply):
    """The assistant message of one chat choice."""

    content: str | list[Json] | None = None
    reasoning: str | None = None
    refusal: str | None = None
    images: tuple[ChatImage, ...] = ()


class ChatChoiceReply(Reply):
    """One chat choice."""

    message: ChatMessage | None = None
    error: ErrorBody | None = None


class ChatReply(Reply):
    """A chat completion."""

    choices: tuple[ChatChoiceReply, ...]


class ImageItem(Reply):
    """One image the image endpoint made."""

    b64_json: str
    media_type: str | None = None


class ImageReply(Reply):
    """The image endpoint's reply."""

    images: tuple[ImageItem, ...] = Field(alias="data")


class VideoJobReply(Reply):
    """A video job's state."""

    id: str
    status: str
    unsigned_urls: tuple[str, ...] = ()
    error: str | None = None


class SegmentReply(Reply):
    """One timed segment of a transcript."""

    start: float | None = None
    end: float | None = None
    text: str
    speaker: str | None = None


class WordReply(Reply):
    """One timed word of a transcript."""

    word: str
    start: float | None = None
    end: float | None = None


class TranscriptionReply(Reply):
    """A transcription; segments and words come only when their timestamps are requested."""

    text: str
    language: str | None = None
    duration: float | None = None
    segments: tuple[SegmentReply, ...] = ()
    words: tuple[WordReply, ...] = ()


class EmbeddingItem(Reply):
    """One embedding vector and the position of its item."""

    embedding: tuple[float, ...]
    index: int


class EmbeddingReply(Reply):
    """The embedding endpoint's reply."""

    vectors: tuple[EmbeddingItem, ...] = Field(alias="data")


class RankItem(Reply):
    """One ranked document and its position among the documents sent."""

    index: int
    relevance_score: float


class RankReply(Reply):
    """The rerank endpoint's reply, highest relevance first."""

    results: tuple[RankItem, ...]


class AnswerReply(Reply):
    """One decision answer; which fields it fills depends on its type."""

    type: str
    noul: float | None = None
    choice: str | None = None
    score: float | None = None
    confidence: float | None = None
    probabilities: Mapping[str, float] = Field(default_factory=dict[str, float])
    legend: Mapping[str, Json] = Field(default_factory=dict[str, Json])


class DecisionReply(Reply):
    """The decision endpoint's reply."""

    answers: Mapping[str, AnswerReply]


__all__ = [
    "AnswerReply",
    "ChatChoiceReply",
    "ChatImage",
    "ChatMessage",
    "ChatReply",
    "DecisionReply",
    "EmbeddingItem",
    "EmbeddingReply",
    "ErrorBody",
    "ErrorMetadata",
    "ErrorReply",
    "ImageItem",
    "ImageReply",
    "ImageUrl",
    "RankItem",
    "RankReply",
    "SegmentReply",
    "TranscriptionReply",
    "VideoJobReply",
    "WordReply",
]

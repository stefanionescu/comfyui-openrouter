"""The parts of OpenRouter's replies the extension reads; unknown fields are ignored."""

from . import Json, Reply
from pydantic import Field
from collections.abc import Mapping


class ErrorMetadata(Reply):
    """Where a provider's own reason sits when OpenRouter only says the provider returned an error.

    Attributes:
        raw: The provider's reply as OpenRouter passed it on, when there is one.

    """

    raw: str | None = None


class ErrorBody(Reply):
    """One OpenRouter error.

    Attributes:
        code: The HTTP status or OpenRouter's error code.
        message: OpenRouter's reason.
        metadata: The provider's own reason, when OpenRouter passes it on.

    """

    code: int | str | None = None
    message: str = ""
    metadata: ErrorMetadata | None = None


class ErrorReply(Reply):
    """An OpenRouter error document.

    Attributes:
        error: The error it describes.

    """

    error: ErrorBody


class ImageUrl(Reply):
    """The address of one image a chat model made.

    Attributes:
        url: A data URL, or a link on the provider's host.

    """

    url: str


class ChatImage(Reply):
    """One image a chat model made.

    Attributes:
        image_url: Where the image is.

    """

    image_url: ImageUrl


class ChatMessage(Reply):
    """The assistant message of one chat choice.

    Attributes:
        content: The answer, as text or as a list of parts.
        reasoning: The model's reasoning, when it shares it.
        refusal: The model's reason for not answering.
        images: The images the model made.

    """

    content: str | list[Json] | None = None
    reasoning: str | None = None
    refusal: str | None = None
    images: tuple[ChatImage, ...] = ()


class ChatChoiceReply(Reply):
    """One chat choice.

    Attributes:
        message: The model's message, when it answered.
        error: The provider's error, when the choice failed after the request succeeded.

    """

    message: ChatMessage | None = None
    error: ErrorBody | None = None


class ChatReply(Reply):
    """A chat completion.

    Attributes:
        choices: The model's answers; the extension reads the first.

    """

    choices: tuple[ChatChoiceReply, ...]


class ImageItem(Reply):
    """One image the image endpoint made.

    Attributes:
        b64_json: The image file, base64-encoded.
        media_type: The file's media type, such as image/png or image/svg+xml.

    """

    b64_json: str
    media_type: str | None = None


class ImageReply(Reply):
    """The image endpoint's reply.

    Attributes:
        images: Every image made, under OpenRouter's name data.

    """

    images: tuple[ImageItem, ...] = Field(alias="data")


class VideoJobReply(Reply):
    """A video job's state.

    Attributes:
        id: The job ID.
        status: Where the job is, such as completed or failed.
        unsigned_urls: The addresses of the finished videos on openrouter.ai.
        error: Why the job failed, when it did.

    """

    id: str
    status: str
    unsigned_urls: tuple[str, ...] = ()
    error: str | None = None


class SegmentReply(Reply):
    """One timed segment of a transcript.

    Attributes:
        start: Start in seconds, when the model times segments.
        end: End in seconds, when the model times segments.
        text: What was said.
        speaker: Who said it, when the model tells speakers apart.

    """

    start: float | None = None
    end: float | None = None
    text: str
    speaker: str | None = None


class WordReply(Reply):
    """One timed word of a transcript.

    Attributes:
        word: The word, as the model wrote it.
        start: Start in seconds.
        end: End in seconds.

    """

    word: str
    start: float | None = None
    end: float | None = None


class TranscriptionReply(Reply):
    """A transcription; segments and words come only when their timestamps are requested.

    Attributes:
        text: The whole transcript.
        language: The language the model detected or was given.
        duration: The clip's length in seconds.
        segments: The timed segments.
        words: The timed words.

    """

    text: str
    language: str | None = None
    duration: float | None = None
    segments: tuple[SegmentReply, ...] = ()
    words: tuple[WordReply, ...] = ()


class EmbeddingItem(Reply):
    """One embedding vector and the position of its item.

    Attributes:
        embedding: The vector.
        index: The position of the item it belongs to, in the order sent.

    """

    embedding: tuple[float, ...]
    index: int


class EmbeddingReply(Reply):
    """The embedding endpoint's reply.

    Attributes:
        vectors: One vector per item, under OpenRouter's name data.

    """

    vectors: tuple[EmbeddingItem, ...] = Field(alias="data")


class RankItem(Reply):
    """One ranked document and its position among the documents sent.

    Attributes:
        index: The document's position, in the order sent.
        relevance_score: How well it matches the query; higher is better.

    """

    index: int
    relevance_score: float


class RankReply(Reply):
    """The rerank endpoint's reply, highest relevance first.

    Attributes:
        results: The ranked documents.

    """

    results: tuple[RankItem, ...]


class AnswerReply(Reply):
    """One decision answer; which fields it fills depends on its type.

    Attributes:
        type: The question type: choice, noul for yes or no, or score.
        noul: The probability of yes, for a yes-or-no question.
        choice: The chosen option, for a one-choice question.
        score: The position on the levels, for a score question.
        confidence: How sure the model is of a choice or a score.
        probabilities: The probability of each option or level.
        legend: The level each score position stands for.

    """

    type: str
    noul: float | None = None
    choice: str | None = None
    score: float | None = None
    confidence: float | None = None
    probabilities: Mapping[str, float] = Field(default_factory=dict[str, float])
    legend: Mapping[str, Json] = Field(default_factory=dict[str, Json])


class DecisionReply(Reply):
    """The decision endpoint's reply.

    Attributes:
        answers: Each answer, keyed by its question's name.

    """

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

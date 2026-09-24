"""Embedding and rank requests and results; items are numbered texts first, then images, in input order."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .options import RequestOptions


@dataclass(frozen=True, slots=True)
class EmbeddingRequest:
    """One embedding request.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        texts: Text items.
        image_urls: PNG data URLs of image items.
        dimensions: Vector length, or 0 for the model's default.
        input_type: A hint such as search_query, or None.
        options: Provider routing and extra fields.

    """

    model_id: str
    texts: tuple[str, ...]
    image_urls: tuple[str, ...]
    dimensions: int
    input_type: str | None
    options: RequestOptions | None


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    """One vector per item, and how similar each item is to the first.

    Attributes:
        vectors: The vectors in item order.
        similarities: The cosine similarity of each vector with the first.

    """

    vectors: tuple[tuple[float, ...], ...]
    similarities: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class RankRequest:
    """One rank request.

    Attributes:
        model_id: The model ID sent to OpenRouter.
        query: What the documents are ranked against.
        texts: Text documents.
        image_urls: PNG data URLs of image documents.
        top_n: How many to keep, or 0 for all.
        options: Provider routing and extra fields.

    """

    model_id: str
    query: str
    texts: tuple[str, ...]
    image_urls: tuple[str, ...]
    top_n: int
    options: RequestOptions | None


@dataclass(frozen=True, slots=True)
class RankedItem:
    """One ranked document.

    Attributes:
        index: The document's item number.
        score: Its relevance.

    """

    index: int
    score: float


@dataclass(frozen=True, slots=True)
class RankResult:
    """The ranked documents, best first.

    Attributes:
        items: The documents in rank order.

    """

    items: tuple[RankedItem, ...]


__all__ = ["EmbeddingRequest", "EmbeddingResult", "RankRequest", "RankResult", "RankedItem"]

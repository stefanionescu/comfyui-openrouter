"""Embedding choices."""

from .inputs import MODEL_DEFAULT

# How a model that embeds queries and documents differently treats the items.
INPUT_TYPES = (MODEL_DEFAULT, "search_query", "search_document")

__all__ = [
    "INPUT_TYPES",
]

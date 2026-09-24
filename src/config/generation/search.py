"""Embedding and rank limits and choices."""

from .inputs import MODEL_DEFAULT

MAX_SEARCH_ITEMS = 256
MAX_SEARCH_IMAGES = 16
MAX_DIMENSIONS = 8192
INPUT_TYPES = (MODEL_DEFAULT, "search_query", "search_document")

__all__ = ["INPUT_TYPES", "MAX_DIMENSIONS", "MAX_SEARCH_IMAGES", "MAX_SEARCH_ITEMS"]

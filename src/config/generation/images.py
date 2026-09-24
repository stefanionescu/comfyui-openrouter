"""Image fields and counts."""

DEFAULT_COMPRESSION = 90
MAX_COMPRESSION = 100
COMPRESSED_FORMATS = ("jpeg", "webp")
MAX_IMAGES = 10
# The image fields in the order the node shows them, with every value OpenRouter's image models take.
FIELD_VALUES = {
    "resolution": ("512", "1K", "2K", "4K"),
    "aspect_ratio": (
        "auto",
        "1:1",
        "1:2",
        "2:1",
        "2:3",
        "3:2",
        "3:4",
        "4:3",
        "4:5",
        "5:4",
        "9:16",
        "16:9",
        "9:21",
        "21:9",
        "1:4",
        "4:1",
        "1:8",
        "8:1",
    ),
    "quality": ("auto", "low", "medium", "high", "xhigh", "max"),
    "background": ("auto", "transparent", "opaque"),
    "output_format": ("png", "jpeg", "webp", "svg"),
}
FIELD_LABELS = {
    "resolution": "resolution",
    "aspect_ratio": "aspect ratio",
    "quality": "quality",
    "background": "background",
    "output_format": "format",
}

__all__ = [
    "COMPRESSED_FORMATS",
    "DEFAULT_COMPRESSION",
    "FIELD_LABELS",
    "FIELD_VALUES",
    "MAX_COMPRESSION",
    "MAX_IMAGES",
]

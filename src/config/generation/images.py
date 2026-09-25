"""Image fields and compression."""

# The compression JPEG and WebP take, in percent.
COMPRESSION = {
    "DEFAULT": 90,
    "MAX": 100,
}

# The formats that take a compression.
COMPRESSED_FORMATS = ("jpeg", "webp")

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
        "9:19.5",
        "19.5:9",
        "9:20",
        "20:9",
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

__all__ = [
    "COMPRESSED_FORMATS",
    "COMPRESSION",
    "FIELD_VALUES",
]

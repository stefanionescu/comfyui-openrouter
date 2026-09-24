"""Image ranges and choices the image model list does not give."""

MAX_REFERENCE_SOCKETS = 16
DEFAULT_COMPRESSION = 90
COMPRESSED_FORMATS = ("jpeg", "webp")
# The image list's enum fields, in the order the node shows them.
ENUM_FIELDS = ("resolution", "aspect_ratio", "quality", "background", "output_format")
# The values a written model ID may choose, since the saved list does not describe it.
ALL_RESOLUTIONS = ("512", "1K", "2K", "4K")
ALL_ASPECT_RATIOS = (
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
)
ALL_QUALITIES = ("auto", "low", "medium", "high", "xhigh", "max")
ALL_BACKGROUNDS = ("auto", "transparent", "opaque")
ALL_FORMATS = ("png", "jpeg", "webp", "svg")
MAX_IMAGES = 10
FIELD_LABELS = {
    "resolution": "resolution",
    "aspect_ratio": "aspect ratio",
    "quality": "quality",
    "background": "background",
    "output_format": "file format",
}

__all__ = [
    "ALL_ASPECT_RATIOS",
    "ALL_BACKGROUNDS",
    "ALL_FORMATS",
    "ALL_QUALITIES",
    "ALL_RESOLUTIONS",
    "COMPRESSED_FORMATS",
    "DEFAULT_COMPRESSION",
    "ENUM_FIELDS",
    "FIELD_LABELS",
    "MAX_IMAGES",
    "MAX_REFERENCE_SOCKETS",
]

"""Image, audio, and video formats the extension sends and reads."""

MAX_IMAGE_SIDE = 8192

# The rank of a ComfyUI IMAGE tensor: batch, height, width, channels.
IMAGE_DIMENSIONS = 4

RGB_CHANNELS = 3

RGBA_CHANNELS = 4

SVG_MEDIA_TYPE = "image/svg+xml"

# An SVG file starts with its root element or an XML declaration, after any leading whitespace.
SVG_STARTS = (b"<svg", b"<?xml")

WAV_FORMAT = "wav"

WAV_CODEC = "pcm_s16le"

WAV_SAMPLE_BYTES = 2


__all__ = [
    "IMAGE_DIMENSIONS",
    "MAX_IMAGE_SIDE",
    "RGBA_CHANNELS",
    "RGB_CHANNELS",
    "SVG_MEDIA_TYPE",
    "SVG_STARTS",
    "WAV_CODEC",
    "WAV_FORMAT",
    "WAV_SAMPLE_BYTES",
]

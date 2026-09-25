"""Image, audio, and video formats the extension sends and reads."""

# A ComfyUI IMAGE tensor: batch, height, width, and three or four channels.
IMAGE_TENSOR = {
    "DIMENSIONS": 4,
    "RGB_CHANNELS": 3,
    "RGBA_CHANNELS": 4,
}

# An SVG file's media type.
SVG_MEDIA_TYPE = "image/svg+xml"

# An SVG file starts with its root element or an XML declaration, after any leading whitespace.
SVG_STARTS = (b"<svg", b"<?xml")

# Video sent inline, as an MP4 data URL.
MP4_URL_PREFIX = "data:video/mp4;base64,"

# Audio sent inline, as a WAV data URL of 16-bit PCM samples.
WAV = {
    "URL_PREFIX": "data:audio/wav;base64,",
    "FORMAT": "wav",
    "CODEC": "pcm_s16le",
}

# Raw PCM a model sends; its rate and channels come as parameters of this media type.
PCM_MEDIA_TYPE = "audio/pcm"

# The bytes of one 16-bit PCM sample.
PCM_SAMPLE_BYTES = 2

__all__ = [
    "IMAGE_TENSOR",
    "MP4_URL_PREFIX",
    "PCM_MEDIA_TYPE",
    "PCM_SAMPLE_BYTES",
    "SVG_MEDIA_TYPE",
    "SVG_STARTS",
    "WAV",
]

"""Messages for media that cannot be sent or read."""

AUDIO_BATCH = "Connect one audio clip, not a batch of several."
AUDIO_EMPTY = "The connected audio has no samples."
AUDIO_UNREADABLE = "The audio OpenRouter returned could not be decoded."
AUDIO_UNWRITABLE = "The connected audio could not be written as WAV. Use mono or stereo audio."
DOWNLOAD_LIMIT = (
    "OpenRouter's reply is larger than the maximum download size of {maximum} MiB in OpenRouter settings. "
    "Raise it or request smaller output."
)
IMAGE_SIZE = (
    "Use images of at most {maximum} pixels per side. Scale larger images down first, for example with Scale "
    "Image to Total Pixels."
)
IMAGE_PIXELS = "The connected image holds values that are not numbers. Check the node that made it."
IMAGE_SHAPE = "Connect a ComfyUI image with three or four color channels."
IMAGE_UNREADABLE = "An image OpenRouter returned could not be decoded."
UPLOAD_LIMIT = (
    "The media in this request is {size} MiB, above the maximum upload size of {maximum} MiB in OpenRouter "
    "settings. Send fewer or smaller files."
)
VIDEO_UNREADABLE = "The connected video could not be written as MP4."

__all__ = [
    "AUDIO_BATCH",
    "AUDIO_EMPTY",
    "AUDIO_UNREADABLE",
    "AUDIO_UNWRITABLE",
    "DOWNLOAD_LIMIT",
    "IMAGE_PIXELS",
    "IMAGE_SHAPE",
    "IMAGE_SIZE",
    "IMAGE_UNREADABLE",
    "UPLOAD_LIMIT",
    "VIDEO_UNREADABLE",
]

"""Video choices and job record limits."""

from .inputs import MODEL_DEFAULT

# The longest duration the node offers, in seconds; 0 sends no duration.
MAX_DURATION = 60
MAX_UPSCALE_FACTOR = 8.0
UPSCALE_STEP = 0.1
MAX_CREATIVITY = 1.0
CREATIVITY_STEP = 0.05
RESOLUTIONS = (MODEL_DEFAULT, "360p", "480p", "720p", "768p", "1080p", "1K", "2K", "4K")
ASPECT_RATIOS = (MODEL_DEFAULT, "16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9", "9:21")
AUDIO_CHOICES = (MODEL_DEFAULT, "on", "off")
DONE_STATUSES = ("completed", "failed", "cancelled", "expired")
# Video: Download lists each job as its ID, model, and start time to the minute, the first 16 characters of the
# ISO time.
JOB_LABEL_SEPARATOR = " · "
JOB_TIME_CHARACTERS = 16

__all__ = [
    "ASPECT_RATIOS",
    "AUDIO_CHOICES",
    "CREATIVITY_STEP",
    "DONE_STATUSES",
    "JOB_LABEL_SEPARATOR",
    "JOB_TIME_CHARACTERS",
    "MAX_CREATIVITY",
    "MAX_DURATION",
    "MAX_UPSCALE_FACTOR",
    "RESOLUTIONS",
    "UPSCALE_STEP",
]

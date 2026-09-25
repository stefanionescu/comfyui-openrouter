"""Video choices and how Video: Download lists jobs."""

from .inputs import MODEL_DEFAULT

UPSCALE_STEP = 0.1
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
    "RESOLUTIONS",
    "UPSCALE_STEP",
]

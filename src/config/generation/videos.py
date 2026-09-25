"""Video choices and how Video: Download lists jobs."""

from .inputs import MODEL_DEFAULT

# How far each click moves the upscale settings.
STEPS = {
    "UPSCALE_FACTOR": 0.1,
    "CREATIVITY": 0.05,
}

# The resolutions video models make.
RESOLUTIONS = (MODEL_DEFAULT, "360p", "480p", "720p", "768p", "1080p", "1K", "2K", "4K")

# The aspect ratios video models make.
ASPECT_RATIOS = (MODEL_DEFAULT, "16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9", "9:21")

# Whether the video has sound.
AUDIO_CHOICES = (MODEL_DEFAULT, "on", "off")

# The statuses of a job that has ended.
DONE_STATUSES = ("completed", "failed", "cancelled", "expired")

# Video: Download lists each job as its ID, model, and start time, joined by this separator.
JOB_LABEL_SEPARATOR = " · "

# The start time to the minute, the first 16 characters of the ISO time.
JOB_TIME_CHARACTERS = 16

__all__ = [
    "ASPECT_RATIOS",
    "AUDIO_CHOICES",
    "DONE_STATUSES",
    "JOB_LABEL_SEPARATOR",
    "JOB_TIME_CHARACTERS",
    "RESOLUTIONS",
    "STEPS",
]

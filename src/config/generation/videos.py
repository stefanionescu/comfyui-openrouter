"""Video defaults, the choices of a written model ID, and job record limits."""

from .inputs import MODEL_DEFAULT

MAX_REFERENCE_IMAGES = 8
MAX_REFERENCE_VIDEOS = 2
MAX_REFERENCE_AUDIO = 2
# The duration range of a written model ID, in seconds; 0 sends no duration.
DURATION_RANGE = (1, 60)
DEFAULT_DURATION = 5
ALL_RESOLUTIONS = (MODEL_DEFAULT, "360p", "480p", "720p", "768p", "1080p", "1K", "2K", "4K")
ALL_ASPECT_RATIOS = (MODEL_DEFAULT, "16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9", "9:21")
AUDIO_CHOICES = (MODEL_DEFAULT, "on", "off")
DONE_STATUSES = ("completed", "failed", "cancelled", "expired")
JOB_FOLDER_NAME = "jobs"
UNCERTAIN_PREFIX = "uncertain-"
MAX_LISTED_JOBS = 100
MAX_JOB_FILE_BYTES = 16_384
SECONDS_PER_MINUTE = 60

__all__ = [
    "ALL_ASPECT_RATIOS",
    "ALL_RESOLUTIONS",
    "AUDIO_CHOICES",
    "DEFAULT_DURATION",
    "DONE_STATUSES",
    "DURATION_RANGE",
    "JOB_FOLDER_NAME",
    "MAX_JOB_FILE_BYTES",
    "MAX_LISTED_JOBS",
    "MAX_REFERENCE_AUDIO",
    "MAX_REFERENCE_IMAGES",
    "MAX_REFERENCE_VIDEOS",
    "SECONDS_PER_MINUTE",
    "UNCERTAIN_PREFIX",
]

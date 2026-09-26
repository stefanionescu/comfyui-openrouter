"""Messages for video jobs, their frames and references, and their recovery."""

FRAMES_BESIDE_REFERENCES = (
    "Connect first or last frames, or references, not both. OpenRouter uses the frames and ignores the references."
)

IMAGE_BATCH = "Connect one image to each frame, not a batch or a list."

JOB_CANCELLED = "OpenRouter cancelled the video job: {reason}"

JOB_EXPIRED = "The video job expired before it finished. Run the node again to start a new job."

JOB_FAILED = "OpenRouter could not make the video: {reason}"

JOB_UNKNOWN = "Choose an unfinished video job from the list. Press R in ComfyUI to refresh the list."

JOB_WAIT_LIMIT = (
    "The video was not ready within the request timeout of {seconds} seconds in OpenRouter settings. "
    "OpenRouter keeps making it; collect it with Video: Download."
)

PROMPT_REQUIRED = "Write a prompt or connect a first frame."

__all__ = [
    "FRAMES_BESIDE_REFERENCES",
    "IMAGE_BATCH",
    "JOB_CANCELLED",
    "JOB_EXPIRED",
    "JOB_FAILED",
    "JOB_UNKNOWN",
    "JOB_WAIT_LIMIT",
    "PROMPT_REQUIRED",
]

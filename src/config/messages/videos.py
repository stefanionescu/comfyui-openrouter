"""Messages for video jobs, their frames and references, and their recovery."""

FRAMES_BESIDE_REFERENCES = (
    "Connect first or last frames, or references, not both. OpenRouter uses the frames and ignores the references."
)
IMAGE_BATCH = "Connect one image for each frame, not a batch."
JOB_CANCELLED = "OpenRouter cancelled the video job: {reason}"
JOB_EXPIRED = "The video job expired before it finished. Run the node again to start a new job."
JOB_FAILED = "OpenRouter could not make the video: {reason}"
JOB_UNKNOWN = "Choose an unfinished video job from the list. Press R in ComfyUI to refresh the list."
JOB_WAIT_LIMIT = (
    "The video was not ready within the maximum video wait of {minutes} minutes in OpenRouter settings. "
    "OpenRouter keeps making it; use Video: Download to collect it."
)
LAST_FRAME_UNSUPPORTED = "{model} does not accept a last frame. Disconnect it or choose a model that does."
PROMPT_REQUIRED = "Write a prompt or connect a first frame."
SUBMIT_HOLD = (
    "An earlier identical video request may have been accepted. Wait {minutes} minutes or check "
    "openrouter.ai/activity before sending it again."
)
SUBMIT_UNCERTAIN = (
    "The connection closed before OpenRouter confirmed the video request. It may be running and billed; check "
    "openrouter.ai/activity. An identical request is held for {minutes} minutes."
)
VIDEO_REFERENCES_RANGE = "Connect at most {maximum} {kind} references."
VIDEO_REFERENCE_KIND = "{model} does not accept {kind} references."
VIDEO_URL_UNEXPECTED = "OpenRouter's video address was not on openrouter.ai, so it was not downloaded."

__all__ = [
    "FRAMES_BESIDE_REFERENCES",
    "IMAGE_BATCH",
    "JOB_CANCELLED",
    "JOB_EXPIRED",
    "JOB_FAILED",
    "JOB_UNKNOWN",
    "JOB_WAIT_LIMIT",
    "LAST_FRAME_UNSUPPORTED",
    "PROMPT_REQUIRED",
    "SUBMIT_HOLD",
    "SUBMIT_UNCERTAIN",
    "VIDEO_REFERENCES_RANGE",
    "VIDEO_REFERENCE_KIND",
    "VIDEO_URL_UNEXPECTED",
]

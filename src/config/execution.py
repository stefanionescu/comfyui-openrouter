"""How a paid run shows ComfyUI's progress bar and notices its cancel."""

# A paid node's progress bar: validated, sent, answered, and outputs built.
PROGRESS_STEPS = 3

# How often a wait checks ComfyUI's cancel, in seconds.
CANCELLATION_POLL_SECONDS = 0.1

__all__ = [
    "CANCELLATION_POLL_SECONDS",
    "PROGRESS_STEPS",
]

"""Chat ranges and choices: media sockets, temperature, token limits, PDF engines, outputs, and voice audio."""

from .inputs import MODEL_DEFAULT

MAX_IMAGE_SOCKETS = 16
MAX_VIDEO_SOCKETS = 4
MAX_AUDIO_SOCKETS = 4
MAX_DOCUMENTS = 8
DEFAULT_TEMPERATURE = 1.0
MAX_TEMPERATURE = 2.0
STEP_TEMPERATURE = 0.05
# The output token limit for a written model ID, which the saved list does not bound.
MAX_OUTPUT_TOKENS = 1_000_000
MAX_CONVERSATION_TURNS = 200
MAX_PROMPT_CHARACTERS = 1_000_000
PDF_ENGINES = (MODEL_DEFAULT, "native", "cloudflare-ai", "mistral-ocr")
ALL_EFFORTS = (MODEL_DEFAULT, "none", "minimal", "low", "medium", "high", "xhigh", "max")
# What each outputs choice asks the model to make besides text.
OUTPUTS = {"text": (), "image and text": ("image",), "audio and text": ("audio",)}
ALL_ASPECT_RATIOS = ("1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9")
# Voice chat models stream only 16-bit PCM, 24,000 Hz, mono; asking for WAV fails with a provider error.
AUDIO_FORMAT = "pcm16"
AUDIO_RATE = 24_000
AUDIO_CHANNELS = 1
DEFAULT_VOICE = "alloy"
ANSWER_SCHEMA_NAME = "answer"
# The document files the input folder may hold, with the media type each is sent as.
DOCUMENT_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".json": "application/json",
}
PDF_MEDIA_TYPE = "application/pdf"

__all__ = [
    "ALL_ASPECT_RATIOS",
    "ALL_EFFORTS",
    "ANSWER_SCHEMA_NAME",
    "AUDIO_CHANNELS",
    "AUDIO_FORMAT",
    "AUDIO_RATE",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_VOICE",
    "DOCUMENT_TYPES",
    "MAX_AUDIO_SOCKETS",
    "MAX_CONVERSATION_TURNS",
    "MAX_DOCUMENTS",
    "MAX_IMAGE_SOCKETS",
    "MAX_OUTPUT_TOKENS",
    "MAX_PROMPT_CHARACTERS",
    "MAX_TEMPERATURE",
    "MAX_VIDEO_SOCKETS",
    "OUTPUTS",
    "PDF_ENGINES",
    "PDF_MEDIA_TYPE",
    "STEP_TEMPERATURE",
]

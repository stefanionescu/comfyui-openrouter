"""The model each paid node starts with."""

DEFAULT_CHAT_MODEL = "google/gemini-3.5-flash"
DEFAULT_IMAGE_MODEL = "google/gemini-3.1-flash-image"
DEFAULT_VIDEO_MODEL = "google/veo-3.1-fast"
DEFAULT_SPEECH_MODEL = "google/gemini-3.1-flash-tts-preview"
DEFAULT_TRANSCRIPTION_MODEL = "openai/whisper-large-v3-turbo"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"
DEFAULT_RANK_MODEL = "cohere/rerank-v3.5"
# A fixed version, so answers stay comparable while thresholds are tuned; ~typesafe/jev-latest follows new releases.
DEFAULT_DECISION_MODEL = "typesafe/jev-1.13"

__all__ = [
    "DEFAULT_CHAT_MODEL",
    "DEFAULT_DECISION_MODEL",
    "DEFAULT_EMBEDDING_MODEL",
    "DEFAULT_IMAGE_MODEL",
    "DEFAULT_RANK_MODEL",
    "DEFAULT_SPEECH_MODEL",
    "DEFAULT_TRANSCRIPTION_MODEL",
    "DEFAULT_VIDEO_MODEL",
]

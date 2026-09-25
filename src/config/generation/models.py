"""The model each paid node starts with, keyed by the endpoint it sends to."""

# The decision model is a fixed version, so answers stay comparable while thresholds are tuned;
# ~typesafe/jev-latest follows new releases.
DEFAULT_MODELS = {
    "chat": "google/gemini-3.5-flash",
    "images": "google/gemini-3.1-flash-image",
    "videos": "google/veo-3.1-fast",
    "speech": "google/gemini-3.1-flash-tts-preview",
    "transcription": "openai/whisper-large-v3-turbo",
    "embeddings": "openai/text-embedding-3-small",
    "rerank": "cohere/rerank-v3.5",
    "decisions": "typesafe/jev-1.13",
}

__all__ = [
    "DEFAULT_MODELS",
]

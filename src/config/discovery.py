"""Public model lists, their size limits, and refresh validation."""

MODELS_URL = "https://openrouter.ai/api/v1/models?output_modalities=all"

IMAGE_MODELS_URL = "https://openrouter.ai/api/v1/images/models"

VIDEO_MODELS_URL = "https://openrouter.ai/api/v1/videos/models"

MODEL_PAGE_URL = "https://openrouter.ai/{model_id}"

SOURCE_USER_AGENT = "comfyui-openrouter/models"

# The full model list measured about 1 MB on 2026-09-23, so the cap leaves room for eight times as many models.
MAX_SOURCE_BYTES = 8_388_608

SOURCE_CHUNK_BYTES = 65_536

SOURCE_TIMEOUT_SECONDS = 30

MAX_MODELS = 4096

# A refresh may add at most this many new IDs, or as many as the previous list held.
MAX_ADDED_MODELS = 64

# A refresh is refused when it lists fewer than the previous count divided by this.
SOURCE_RETENTION_DIVISOR = 2

MAX_LIST_BYTES = 33_554_432

CHECK_POLL_SECONDS = 60

CHECK_TIMEOUT_SECONDS = 90

LIST_FILE_NAME = "list.json"

LIST_FOLDER_NAME = "models"

# The node each endpoint's models appear in, as the models dialog names it.
ENDPOINT_NODES = {
    "chat": "Chat: Ask",
    "images": "Image: Generate",
    "videos": "Video: Generate",
    "speech": "Audio: Speak",
    "transcription": "Audio: Transcribe",
    "embeddings": "Search: Embed",
    "rerank": "Search: Rank",
    "decisions": "Decision: Ask",
}

# Price lines per token or character, and the unit the dialog shows for each.
TOKEN_PRICE_UNITS = {"prompt": "input tokens", "completion": "output tokens", "request": "request"}
SPEECH_PRICE_UNITS = {"prompt": "input characters"}
VIDEO_PRICE_UNIT = "video second"

__all__ = [
    "CHECK_POLL_SECONDS",
    "CHECK_TIMEOUT_SECONDS",
    "ENDPOINT_NODES",
    "IMAGE_MODELS_URL",
    "LIST_FILE_NAME",
    "LIST_FOLDER_NAME",
    "MAX_ADDED_MODELS",
    "MAX_LIST_BYTES",
    "MAX_MODELS",
    "MAX_SOURCE_BYTES",
    "MODELS_URL",
    "MODEL_PAGE_URL",
    "SOURCE_CHUNK_BYTES",
    "SOURCE_RETENTION_DIVISOR",
    "SOURCE_TIMEOUT_SECONDS",
    "SOURCE_USER_AGENT",
    "SPEECH_PRICE_UNITS",
    "TOKEN_PRICE_UNITS",
    "VIDEO_MODELS_URL",
    "VIDEO_PRICE_UNIT",
]

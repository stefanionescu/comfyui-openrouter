"""OpenRouter's addresses, attribution, reply limits, and the request fields each endpoint accepts."""

from .generation.inputs import MODEL_DEFAULT

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
IMAGES_URL = "https://openrouter.ai/api/v1/images"
VIDEOS_URL = "https://openrouter.ai/api/v1/videos"
VIDEO_JOB_URL = "https://openrouter.ai/api/v1/videos/{job_id}"
# A finished job's first video.
VIDEO_CONTENT_URL = "https://openrouter.ai/api/v1/videos/{job_id}/content"
SPEECH_URL = "https://openrouter.ai/api/v1/audio/speech"
TRANSCRIPTION_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"
RERANK_URL = "https://openrouter.ai/api/v1/rerank"
DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
# The public listings, read without the key: one model, one image model's providers, and every video model. An
# unknown ID returns 404.
MODEL_URL = "https://openrouter.ai/api/v1/models/{model_id}/endpoints"
IMAGE_MODEL_URL = "https://openrouter.ai/api/v1/images/models/{model_id}/endpoints"
VIDEO_MODELS_URL = "https://openrouter.ai/api/v1/videos/models"
# How the model check names what a model reads or makes, and the image and video fields whose name differs from
# the node's label.
MEDIA_LABELS = {"image": "images", "video": "video", "audio": "audio"}
# A chat model follows an answer schema when a provider lists either field.
SCHEMA_PARAMETERS = ("structured_outputs", "response_format")
FIELD_NAMES = {
    "n": "count",
    "input_references": "references",
    "output_format": "format",
    "output_compression": "compression",
}

# OpenRouter attributes usage to an address; the Registry page's name is fixed before the first release.
ATTRIBUTION_URL = "https://registry.comfy.org/nodes/comfyui-openrouter"
ATTRIBUTION_TITLE = "ComfyUI OpenRouter"
ATTRIBUTION_CATEGORIES = "image-gen,video-gen"

REPLY_CHUNK_BYTES = 65_536
MAX_ERROR_BYTES = 65_536

MAX_REASON_CHARACTERS = 300
# A reason that ends otherwise gets a full stop.
REASON_ENDINGS = (".", "!", "?", "…")
CANCELLATION_POLL_SECONDS = 0.1
# A paid node's progress bar: validated, sent, answered, and outputs built.
PROGRESS_STEPS = 3

# The provider fields each endpoint accepts.
ROUTING_FIELDS = {
    "chat": ("order", "only", "ignore", "sort", "allow_fallbacks", "data_collection", "zdr", "max_price", "options"),
    "images": ("order", "only", "ignore", "sort", "allow_fallbacks", "options"),
    "videos": ("options",),
    "speech": ("options",),
    "transcription": ("options",),
    "embeddings": (
        "order",
        "only",
        "ignore",
        "sort",
        "allow_fallbacks",
        "data_collection",
        "zdr",
        "max_price",
        "options",
    ),
    "rerank": ("order", "only", "ignore", "sort", "allow_fallbacks", "data_collection", "zdr", "max_price", "options"),
    "decisions": (
        "order",
        "only",
        "ignore",
        "sort",
        "allow_fallbacks",
        "data_collection",
        "zdr",
        "max_price",
        "options",
    ),
}
# How Request Options names the provider fields whose OpenRouter name differs, for its messages.
ROUTING_LABELS = {
    "order": "provider",
    "data_collection": "data collection",
    "zdr": "zero data retention",
    "max_price": "price limits",
    "options": "provider options",
}
# The body fields each node sets itself, which extra fields may not replace. Provider routing is set only through
# Request Options, and chat's models and route would name backup models.
RESERVED_FIELDS = {
    "chat": ("model", "messages", "stream", "modalities", "audio", "provider", "models", "route"),
    "images": ("model", "prompt", "input_references", "stream", "provider"),
    "videos": ("model", "prompt", "frame_images", "input_references", "callback_url", "provider"),
    "speech": ("model", "input", "input_references", "response_format", "provider"),
    "transcription": ("model", "input_audio", "provider"),
    "embeddings": ("model", "input", "encoding_format", "provider"),
    "rerank": ("model", "query", "documents", "provider"),
    "decisions": ("model", "state", "questions", "provider"),
}

SORT_CHOICES = (MODEL_DEFAULT, "price", "throughput", "latency")
COLLECTION_CHOICES = (MODEL_DEFAULT, "allow", "deny")
ENDPOINT_LABELS = {
    "chat": "chat",
    "images": "image",
    "videos": "video",
    "speech": "speech",
    "transcription": "transcription",
    "embeddings": "embedding",
    "rerank": "rank",
    "decisions": "decision",
}
# What a model must make, in OpenRouter's output_modalities names, to suit each endpoint.
MODEL_OUTPUTS = {
    "chat": ("text", "image", "audio"),
    "images": ("image",),
    "videos": ("video",),
    "speech": ("speech",),
    "transcription": ("transcription",),
    "embeddings": ("embeddings",),
    "rerank": ("rerank",),
    "decisions": ("decisions",),
}
# The price caps of Request Options, in USD per million tokens, and the precision OpenRouter accepts.
PRICE_STEP = 0.01
PRICE_PRECISION = "0.000001"

__all__ = [
    "ATTRIBUTION_CATEGORIES",
    "ATTRIBUTION_TITLE",
    "ATTRIBUTION_URL",
    "CANCELLATION_POLL_SECONDS",
    "CHAT_URL",
    "COLLECTION_CHOICES",
    "DECISIONS_URL",
    "EMBEDDINGS_URL",
    "ENDPOINT_LABELS",
    "FIELD_NAMES",
    "IMAGES_URL",
    "IMAGE_MODEL_URL",
    "MAX_ERROR_BYTES",
    "MAX_REASON_CHARACTERS",
    "MEDIA_LABELS",
    "MODEL_OUTPUTS",
    "MODEL_URL",
    "PRICE_PRECISION",
    "PRICE_STEP",
    "PROGRESS_STEPS",
    "REASON_ENDINGS",
    "REPLY_CHUNK_BYTES",
    "RERANK_URL",
    "RESERVED_FIELDS",
    "ROUTING_FIELDS",
    "ROUTING_LABELS",
    "SCHEMA_PARAMETERS",
    "SORT_CHOICES",
    "SPEECH_URL",
    "TRANSCRIPTION_URL",
    "VIDEOS_URL",
    "VIDEO_CONTENT_URL",
    "VIDEO_JOB_URL",
    "VIDEO_MODELS_URL",
]

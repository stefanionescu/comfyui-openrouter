"""OpenRouter's addresses, attribution, reply limits, retries, and the request fields each endpoint accepts."""

from .generation.inputs import MODEL_DEFAULT

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
IMAGES_URL = "https://openrouter.ai/api/v1/images"
VIDEOS_URL = "https://openrouter.ai/api/v1/videos"
VIDEO_JOB_URL = "https://openrouter.ai/api/v1/videos/{job_id}"
# The key is sent only to video content addresses under this prefix.
VIDEO_CONTENT_PREFIX = "https://openrouter.ai/api/v1/videos/"
SPEECH_URL = "https://openrouter.ai/api/v1/audio/speech"
TRANSCRIPTION_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"
RERANK_URL = "https://openrouter.ai/api/v1/rerank"
DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
# The public listing of one model, read without the key; an unknown ID returns 404.
MODEL_URL = "https://openrouter.ai/api/v1/models/{model_id}/endpoints"

# OpenRouter attributes usage to an address; the Registry page's name is fixed before the first release.
ATTRIBUTION_URL = "https://registry.comfy.org/nodes/comfyui-openrouter"
ATTRIBUTION_TITLE = "ComfyUI OpenRouter"
ATTRIBUTION_CATEGORIES = "image-gen,video-gen"

REPLY_CHUNK_BYTES = 65_536
MAX_ERROR_BYTES = 65_536

# Only requests that bill nothing are retried: model checks, video status, and video content.
GET_ATTEMPTS = 3
MIN_RETRY_SECONDS = 1
MAX_RETRY_SECONDS = 30
RETRY_STATUSES = (408, 429, 500, 502, 503, 504, 524, 529)

MAX_REASON_CHARACTERS = 300
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
    "embeddings": ("order", "only", "ignore", "sort", "allow_fallbacks", "data_collection", "zdr", "max_price"),
    "rerank": ("order", "only", "ignore", "sort", "allow_fallbacks", "data_collection", "zdr", "max_price"),
    "decisions": ("order", "only", "ignore", "sort", "allow_fallbacks", "data_collection", "zdr", "max_price"),
}
# The body fields each node sets itself, which extra fields may not replace.
RESERVED_FIELDS = {
    "chat": ("model", "messages", "stream", "modalities", "audio"),
    "images": ("model", "prompt", "input_references", "stream"),
    "videos": ("model", "prompt", "frame_images", "input_references", "callback_url"),
    "speech": ("model", "input", "input_references", "response_format"),
    "transcription": ("model", "input_audio"),
    "embeddings": ("model", "input", "encoding_format"),
    "rerank": ("model", "query", "documents"),
    "decisions": ("model", "state", "questions"),
}

SORT_CHOICES = (MODEL_DEFAULT, "price", "throughput", "latency")
YES_NO_CHOICES = (MODEL_DEFAULT, "yes", "no")
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
MAX_PROVIDERS = 32
# The price caps of Request Options, in USD per million tokens, and the precision OpenRouter accepts.
MAX_PRICE = 1000.0
PRICE_STEP = 0.01
PRICE_PRECISION = "0.000001"
MAX_OPTION_BYTES = 65_536

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
    "GET_ATTEMPTS",
    "IMAGES_URL",
    "MAX_ERROR_BYTES",
    "MAX_OPTION_BYTES",
    "MAX_PRICE",
    "MAX_PROVIDERS",
    "MAX_REASON_CHARACTERS",
    "MAX_RETRY_SECONDS",
    "MIN_RETRY_SECONDS",
    "MODEL_OUTPUTS",
    "MODEL_URL",
    "PRICE_PRECISION",
    "PRICE_STEP",
    "PROGRESS_STEPS",
    "REPLY_CHUNK_BYTES",
    "RERANK_URL",
    "RESERVED_FIELDS",
    "RETRY_STATUSES",
    "ROUTING_FIELDS",
    "SORT_CHOICES",
    "SPEECH_URL",
    "TRANSCRIPTION_URL",
    "VIDEOS_URL",
    "VIDEO_CONTENT_PREFIX",
    "VIDEO_JOB_URL",
    "YES_NO_CHOICES",
]

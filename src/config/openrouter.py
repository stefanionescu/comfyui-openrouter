"""OpenRouter's addresses, attribution, reply limits, and the request fields each endpoint accepts."""

from .generation.inputs import MODEL_DEFAULT

# The paid endpoints, keyed by endpoint.
ENDPOINT_URLS = {
    "chat": "https://openrouter.ai/api/v1/chat/completions",
    "images": "https://openrouter.ai/api/v1/images",
    "videos": "https://openrouter.ai/api/v1/videos",
    "speech": "https://openrouter.ai/api/v1/audio/speech",
    "transcription": "https://openrouter.ai/api/v1/audio/transcriptions",
    "embeddings": "https://openrouter.ai/api/v1/embeddings",
    "rerank": "https://openrouter.ai/api/v1/rerank",
    "decisions": "https://openrouter.ai/api/alpha/decisions",
}

# A video job's status, and its first finished video.
VIDEO_JOB_URLS = {
    "STATUS": "https://openrouter.ai/api/v1/videos/{job_id}",
    "CONTENT": "https://openrouter.ai/api/v1/videos/{job_id}/content",
}

# The public listings, read without the key: one model, one image model's providers, and every video model. An
# unknown ID returns 404.
LISTING_URLS = {
    "MODEL": "https://openrouter.ai/api/v1/models/{model_id}/endpoints",
    "IMAGE_MODEL": "https://openrouter.ai/api/v1/images/models/{model_id}/endpoints",
    "VIDEO_MODELS": "https://openrouter.ai/api/v1/videos/models",
}

# OpenRouter attributes usage to this address and title, under the categories it recognizes for what the
# extension makes. The Registry page's name is fixed before the first release.
ATTRIBUTION_HEADERS = {
    "HTTP-Referer": "https://registry.comfy.org/nodes/comfyui-openrouter",
    "X-OpenRouter-Title": "ComfyUI OpenRouter",
    "X-OpenRouter-Categories": "image-gen,video-gen,audio-gen",
}

# A reply is read in chunks, and a failed one only this far.
REPLY_BYTES = {
    "CHUNK": 65_536,
    "MAX_ERROR": 65_536,
}

# A failed reply's reason is cut to this length.
MAX_REASON_CHARACTERS = 300

# A reason that ends otherwise gets a full stop.
REASON_ENDINGS = (".", "!", "?", "…")

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

# A chat model follows an answer schema when a provider lists either field.
SCHEMA_PARAMETERS = ("structured_outputs", "response_format")

# How messages name each endpoint.
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

# How messages name the media a model reads.
MEDIA_LABELS = {"image": "images", "video": "video", "audio": "audio"}

# How messages and nodes name the image and video fields whose OpenRouter name reads differently; any other
# field drops its underscores.
FIELD_LABELS = {
    "n": "count",
    "input_references": "references",
    "output_format": "format",
    "output_compression": "compression",
}

# Every provider field OpenRouter's routing takes.
ALL_ROUTING_FIELDS = (
    "order",
    "only",
    "ignore",
    "sort",
    "allow_fallbacks",
    "data_collection",
    "zdr",
    "max_price",
    "options",
)

# The provider fields each endpoint accepts. Every endpoint that accepts allow_fallbacks gets it false.
ROUTING_FIELDS = {
    "chat": ALL_ROUTING_FIELDS,
    "images": ("order", "only", "ignore", "sort", "allow_fallbacks", "options"),
    "videos": ("options",),
    "speech": ("options",),
    "transcription": ("options",),
    "embeddings": ALL_ROUTING_FIELDS,
    "rerank": ALL_ROUTING_FIELDS,
    "decisions": ALL_ROUTING_FIELDS,
}

# How Request Options names the provider fields whose OpenRouter name differs, for its messages.
ROUTING_LABELS = {
    "order": "provider",
    "data_collection": "data collection",
    "zdr": "zero data retention",
    "max_price": "price limits",
    "options": "provider options",
}

# The body fields each node sets itself, which extra fields may not replace. Provider routing is set only
# through Request Options, and chat's models and route would name backup models.
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

# OpenRouter's provider sort values.
SORT_CHOICES = (MODEL_DEFAULT, "price", "throughput", "latency")

# OpenRouter's data collection values.
COLLECTION_CHOICES = (MODEL_DEFAULT, "allow", "deny")

# The price caps of Request Options, in USD per million tokens, move a cent at a time.
PRICE_STEP = 0.01

# The precision OpenRouter accepts for a price cap.
PRICE_PRECISION = "0.000001"

__all__ = [
    "ALL_ROUTING_FIELDS",
    "ATTRIBUTION_HEADERS",
    "COLLECTION_CHOICES",
    "ENDPOINT_LABELS",
    "ENDPOINT_URLS",
    "FIELD_LABELS",
    "LISTING_URLS",
    "MAX_REASON_CHARACTERS",
    "MEDIA_LABELS",
    "MODEL_OUTPUTS",
    "PRICE_PRECISION",
    "PRICE_STEP",
    "REASON_ENDINGS",
    "REPLY_BYTES",
    "RESERVED_FIELDS",
    "ROUTING_FIELDS",
    "ROUTING_LABELS",
    "SCHEMA_PARAMETERS",
    "SORT_CHOICES",
    "VIDEO_JOB_URLS",
]

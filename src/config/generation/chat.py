"""Chat: Ask and Chat: Attach Document choices."""

from .inputs import MODEL_DEFAULT

# The temperature dropdown's input and choice names: model default sends none, and set sends its value.
TEMPERATURE_CHOICE = {
    "INPUT": "temperature",
    "SET": "set",
    "VALUE": "value",
}

# A set temperature, in OpenRouter's documented range.
TEMPERATURE = {
    "DEFAULT": 1.0,
    "MAX": 2.0,
    "STEP": 0.05,
}

# How much a reasoning model thinks.
EFFORTS = (MODEL_DEFAULT, "none", "minimal", "low", "medium", "high", "xhigh", "max")

# What each outputs choice asks the model to make besides text.
OUTPUTS = {"text": (), "image and text": ("image",), "audio and text": ("audio",)}

# The shape of the images a chat model makes.
IMAGE_ASPECT_RATIOS = (MODEL_DEFAULT, "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9")

# How OpenRouter reads PDFs.
PDF_ENGINES = (MODEL_DEFAULT, "native", "cloudflare-ai", "mistral-ocr")

# The name an answer schema is sent under.
ANSWER_SCHEMA_NAME = "answer"

# The voice a spoken reply starts with, and the format voice chat models stream; asking for WAV fails with a
# provider error.
VOICE = {
    "DEFAULT": "alloy",
    "FORMAT": "pcm16",
}

# Voice chat models stream 16-bit PCM at this rate, in mono.
VOICE_AUDIO = {
    "SAMPLE_RATE": 24_000,
    "CHANNELS": 1,
}

# A PDF goes to OpenRouter's PDF engine; any other document goes as text.
PDF_MEDIA_TYPE = "application/pdf"

# The document files the input folder may hold, with the media type each is sent as.
DOCUMENT_TYPES = {
    ".pdf": PDF_MEDIA_TYPE,
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".json": "application/json",
}

__all__ = [
    "ANSWER_SCHEMA_NAME",
    "DOCUMENT_TYPES",
    "EFFORTS",
    "IMAGE_ASPECT_RATIOS",
    "OUTPUTS",
    "PDF_ENGINES",
    "PDF_MEDIA_TYPE",
    "TEMPERATURE",
    "TEMPERATURE_CHOICE",
    "VOICE",
    "VOICE_AUDIO",
]

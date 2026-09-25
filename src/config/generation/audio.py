"""Audio: Speak and Audio: Transcribe choices."""

# Most speech models send PCM, and Google's Gemini voices send nothing else; MiniMax sends only MP3.
SPEECH_FORMATS = ("pcm", "mp3")

# The format Audio: Speak starts with, and a voice of the default speech model, which needs one; other models
# name their own voices.
SPEECH_DEFAULTS = {
    "FORMAT": "pcm",
    "VOICE": "Kore",
}

# OpenAI's documented speed range; other providers ignore the speed.
SPEED = {
    "DEFAULT": 1.0,
    "MIN": 0.25,
    "MAX": 4.0,
    "STEP": 0.05,
}

# The timestamps Audio: Transcribe asks for.
TIMESTAMP_CHOICES = ("none", "segments", "words and segments")

# OpenAI's documented transcription temperature range.
TRANSCRIPTION_TEMPERATURE = {
    "MAX": 1.0,
    "STEP": 0.05,
}

__all__ = [
    "SPEECH_DEFAULTS",
    "SPEECH_FORMATS",
    "SPEED",
    "TIMESTAMP_CHOICES",
    "TRANSCRIPTION_TEMPERATURE",
]

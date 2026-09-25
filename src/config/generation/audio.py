"""Speech formats and speeds, and transcription choices."""

# Most speech models send PCM, and Google's Gemini voices send nothing else; MiniMax sends only MP3.
SPEECH_FORMATS = ("pcm", "mp3")
DEFAULT_SPEECH_FORMAT = "pcm"
# A voice of the default speech model, which needs one; other models name their own voices.
DEFAULT_SPEECH_VOICE = "Kore"
PCM_MEDIA_TYPE = "audio/pcm"
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.25
MAX_SPEED = 4.0
SPEED_STEP = 0.05
TIMESTAMP_CHOICES = ("none", "segments", "words and segments")
MAX_TRANSCRIPTION_TEMPERATURE = 1.0
TRANSCRIPTION_TEMPERATURE_STEP = 0.05

__all__ = [
    "DEFAULT_SPEECH_FORMAT",
    "DEFAULT_SPEECH_VOICE",
    "DEFAULT_SPEED",
    "MAX_SPEED",
    "MAX_TRANSCRIPTION_TEMPERATURE",
    "MIN_SPEED",
    "PCM_MEDIA_TYPE",
    "SPEECH_FORMATS",
    "SPEED_STEP",
    "TIMESTAMP_CHOICES",
    "TRANSCRIPTION_TEMPERATURE_STEP",
]

"""Speech formats and speeds, and transcription choices."""

# Every speech model tested sends PCM except MiniMax, and Google's Gemini voices send nothing else.
SPEECH_FORMATS = ("pcm", "mp3")
DEFAULT_SPEECH_FORMAT = "pcm"
MP3_ONLY_PREFIXES = ("minimax/",)
PCM_MEDIA_TYPE = "audio/pcm"
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.25
MAX_SPEED = 4.0
MAX_SPEECH_CHARACTERS = 100_000
# The voice sample limit, 15 MiB of decoded audio.
MAX_VOICE_SAMPLE_BYTES = 15_728_640
TIMESTAMP_CHOICES = ("none", "segments", "words and segments")
MAX_TRANSCRIPTION_TEMPERATURE = 1.0

__all__ = [
    "DEFAULT_SPEECH_FORMAT",
    "DEFAULT_SPEED",
    "MAX_SPEECH_CHARACTERS",
    "MAX_SPEED",
    "MAX_TRANSCRIPTION_TEMPERATURE",
    "MAX_VOICE_SAMPLE_BYTES",
    "MIN_SPEED",
    "MP3_ONLY_PREFIXES",
    "PCM_MEDIA_TYPE",
    "SPEECH_FORMATS",
    "TIMESTAMP_CHOICES",
]

"""The audio workflows: read text aloud, transcribe, clone a voice, and translate a recording."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import AUDIO, PREVIEW, SAVE_TEXT, SAVE_AUDIO, PREVIEW_AUDIO

SPEAK = f"{NODE_PREFIX}AudioSpeak"
TRANSCRIBE = f"{NODE_PREFIX}AudioTranscribe"

READ_TEXT_ALOUD = Workflow(
    slug="audio-01-read-text-aloud",
    nodes=(
        Node("speak", SPEAK, {"text": "Welcome to ComfyUI with OpenRouter."}, is_paid=True),
        Node("save", SAVE_AUDIO, {"filename_prefix": "audio/openrouter/audio-01-read-text-aloud"}),
    ),
    links=(("speak.audio", "save.audio"),),
    stacks=((Group(SHARED_TEXTS["speech"], (("speak",), ("save",)), STAGE_COLOUR),),),
)

TRANSCRIBE_A_RECORDING = Workflow(
    slug="audio-02-transcribe-a-recording",
    nodes=(
        Node("recording", AUDIO, {"audio": ""}),
        Node("transcribe", TRANSCRIBE, {"timestamps": "segments"}, is_paid=True),
        Node("save", SAVE_TEXT, {"filename_prefix": "text/openrouter/audio-02-transcribe-a-recording"}),
        Node("subtitles", PREVIEW, title="Subtitles"),
    ),
    links=(
        ("recording.AUDIO", "transcribe.audio"),
        ("transcribe.text", "save.text"),
        ("transcribe.subtitles", "subtitles.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("recording",),)),),
        (Group(SHARED_TEXTS["transcript"], (("transcribe",), ("save", "subtitles")), STAGE_COLOUR),),
    ),
)

CLONE_A_VOICE = Workflow(
    slug="audio-03-clone-a-voice",
    nodes=(
        Node("sample", AUDIO, {"audio": ""}),
        Node("speak", SPEAK, {"model": "fish-audio/s2.1-pro", "text": "This is my cloned voice."}, is_paid=True),
        Node("listen", PREVIEW_AUDIO),
    ),
    links=(("sample.AUDIO", "speak.voice_sample"), ("speak.audio", "listen.audio")),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("sample",),)),),
        (Group(SHARED_TEXTS["speech"], (("speak",), ("listen",)), STAGE_COLOUR),),
    ),
)

TRANSLATE_A_RECORDING = Workflow(
    slug="audio-04-translate-a-recording",
    nodes=(
        Node("recording", AUDIO, {"audio": ""}),
        Node("transcribe", TRANSCRIBE, is_paid=True),
        Node(
            "translate",
            f"{NODE_PREFIX}ChatAsk",
            {"system": "Translate the text into Spanish. Answer with the translation only."},
            is_paid=True,
        ),
        Node("speak", SPEAK, is_paid=True),
        Node("save", SAVE_AUDIO, {"filename_prefix": "audio/openrouter/audio-04-translate-a-recording"}),
    ),
    links=(
        ("recording.AUDIO", "transcribe.audio"),
        ("transcribe.text", "translate.prompt"),
        ("translate.text", "speak.text"),
        ("speak.audio", "save.audio"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("recording",),)),),
        (Group(SHARED_TEXTS["transcript"], (("transcribe",),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["ask"], (("translate",),), STAGE_COLOUR),),
        (Group(SHARED_TEXTS["speech"], (("speak",), ("save",)), STAGE_COLOUR),),
    ),
)

AUDIO_WORKFLOWS = (READ_TEXT_ALOUD, TRANSCRIBE_A_RECORDING, CLONE_A_VOICE, TRANSLATE_A_RECORDING)

__all__ = ["AUDIO_WORKFLOWS"]

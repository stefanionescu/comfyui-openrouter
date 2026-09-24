"""The audio workflows: triage a voicemail with Jev and speak a callback, and dub a clip in its own voice."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
from scripts.config import TEXT, AUDIO, FORMAT, SWITCH, PREVIEW, SAVE_TEXT, SAVE_AUDIO

ASK = f"{NODE_PREFIX}ChatAsk"
SPEAK = f"{NODE_PREFIX}AudioSpeak"
TRANSCRIBE = f"{NODE_PREFIX}AudioTranscribe"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
TRANSCRIBER = "assemblyai/universal-3-5-pro"

TRIAGE_VOICEMAIL = Workflow(
    slug="audio-01-triage-a-voicemail",
    nodes=(
        Node("voicemail", AUDIO, {"audio": ""}, title="Voicemail"),
        Node(
            "department",
            QUESTION,
            {
                "name": "department",
                "instructions": "Which department should call back?",
                "answer_type": "one choice",
                "answer_type.options": (
                    "sales: New orders, quotes, and product questions.\n"
                    "support: Faults, repairs, and how-to questions.\n"
                    "billing: Charges, refunds, and invoices."
                ),
            },
            title="Department",
        ),
        Node(
            "callback",
            QUESTION,
            {"name": "callback", "instructions": "Does the caller ask to be called back?"},
            title="Call Back",
        ),
        Node(
            "urgency",
            QUESTION,
            {
                "name": "urgency",
                "instructions": "How urgent is the call?",
                "answer_type": "score",
                "answer_type.levels": "This week\nToday\nWithin the hour",
            },
            title="Urgency",
        ),
        Node("transcribe", TRANSCRIBE, {"model": TRANSCRIBER}, title="Transcribe", is_paid=True),
        Node("save_transcript", SAVE_TEXT, {"filename_prefix": "voicemail/transcript"}, title="Save the Transcript"),
        Node("decide", DECIDE, title="Triage the Call", is_paid=True),
        Node("read_department", READ, {"question": "department"}, title="Read Department"),
        Node("read_callback", READ, {"question": "callback"}, title="Read Call Back"),
        Node("summary", PREVIEW, title="Triage Summary"),
        Node(
            "request",
            FORMAT,
            {
                "f_string": (
                    "You work in the {b} team. Write what you say when you call this customer back: under 60 words, "
                    "friendly, and answering what they asked.\n\nTheir voicemail:\n{a}"
                )
            },
            title="Script Request",
        ),
        Node("script", ASK, {"model": "openai/gpt-6-luna"}, title="Write the Script", is_paid=True),
        Node(
            "speak",
            SPEAK,
            {"model": "google/gemini-3.8-flash-tts", "model.voice": "Kore"},
            title="Speak the Script",
            is_paid=True,
        ),
        Node("call_back", TEXT, {"value": "voicemail/call-back"}, title="Call-Back Folder"),
        Node("no_call", TEXT, {"value": "voicemail/no-call-back"}, title="No-Call Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_AUDIO, title="Save the Script"),
    ),
    links=(
        ("voicemail.AUDIO", "transcribe.audio"),
        ("transcribe.text", "save_transcript.text"),
        ("transcribe.text", "decide.situation"),
        ("department.questions", "callback.questions"),
        ("callback.questions", "urgency.questions"),
        ("urgency.questions", "decide.questions"),
        ("decide.answers", "read_department.answers"),
        ("decide.answers", "read_callback.answers"),
        ("decide.summary", "summary.source"),
        ("transcribe.text", "request.values.a"),
        ("read_department.answer", "request.values.b"),
        ("request.STRING", "script.prompt"),
        ("script.text", "speak.text"),
        ("read_callback.is_yes", "folder.switch"),
        ("call_back.STRING", "folder.on_true"),
        ("no_call.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("speak.audio", "save.audio"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("voicemail",), ("department", "callback", "urgency"))),),
        (
            Group(
                SHARED_TEXTS["transcript"],
                (("transcribe", "save_transcript"), ("decide", "read_department", "read_callback", "summary")),
                STAGE_COLOUR,
            ),
        ),
        (
            Group(
                SHARED_TEXTS["reply"],
                (("request", "script", "speak"), ("call_back", "no_call", "folder", "save")),
                STAGE_COLOUR,
            ),
        ),
    ),
)

DUB_CLIP = Workflow(
    slug="audio-02-dub-a-clip-in-your-voice",
    nodes=(
        Node("clip", AUDIO, {"audio": ""}, title="Your Clip"),
        Node(
            "faithful",
            QUESTION,
            {
                "name": "faithful",
                "instructions": (
                    "Does the Spanish translation say the same as the original, with nothing added or left out?"
                ),
            },
            title="Faithful",
        ),
        Node(
            "transcribe", TRANSCRIBE, {"model": TRANSCRIBER, "timestamps": "segments"}, title="Transcribe", is_paid=True
        ),
        Node("save_subtitles", SAVE_TEXT, {"filename_prefix": "dub/subtitles"}, title="Save the Subtitles"),
        Node(
            "translate",
            ASK,
            {
                "model": "openai/gpt-6-sol",
                "system": (
                    "Translate the text into natural Spanish. Keep the meaning and the tone. Answer with the "
                    "translation only."
                ),
            },
            title="Translate",
            is_paid=True,
        ),
        Node(
            "situation",
            FORMAT,
            {"f_string": "Original:\n{a}\n\nSpanish translation:\n{b}"},
            title="Original and Translation",
        ),
        Node("decide", DECIDE, title="Check the Translation", is_paid=True),
        Node("read", READ, {"question": "faithful"}, title="Read Faithful"),
        Node("speak", SPEAK, {"model": "fish-audio/s2.1-pro"}, title="Speak in Your Voice", is_paid=True),
        Node("approved", TEXT, {"value": "dub/approved"}, title="Approved Folder"),
        Node("review", TEXT, {"value": "dub/review"}, title="Review Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_AUDIO, title="Save the Dub"),
    ),
    links=(
        ("clip.AUDIO", "transcribe.audio"),
        ("clip.AUDIO", "speak.voice_sample"),
        ("transcribe.text", "speak.sample_transcript"),
        ("transcribe.subtitles", "save_subtitles.text"),
        ("transcribe.text", "translate.prompt"),
        ("transcribe.text", "situation.values.a"),
        ("translate.text", "situation.values.b"),
        ("translate.text", "speak.text"),
        ("situation.STRING", "decide.situation"),
        ("faithful.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("read.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("speak.audio", "save.audio"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("clip", "faithful"),)),),
        (
            Group(
                SHARED_TEXTS["transcript"], (("transcribe", "save_subtitles"), ("translate", "situation")), STAGE_COLOUR
            ),
        ),
        (
            Group(
                SHARED_TEXTS["dub"],
                (("decide", "read"), ("speak",), ("approved", "review", "folder", "save")),
                STAGE_COLOUR,
            ),
        ),
    ),
)

AUDIO_WORKFLOWS = (TRIAGE_VOICEMAIL, DUB_CLIP)

__all__ = ["AUDIO_WORKFLOWS"]

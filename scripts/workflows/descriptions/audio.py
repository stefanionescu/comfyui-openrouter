"""The audio workflows: triage a voicemail with Jev and speak a reply, and dub a clip in the same voice."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, AUDIO_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.config import TEXT, AUDIO, FORMAT, SWITCH, PREVIEW, SAVE_TEXT, SAVE_AUDIO

ASK = f"{NODE_PREFIX}ChatAsk"
SPEAK = f"{NODE_PREFIX}AudioSpeak"
TRANSCRIBE = f"{NODE_PREFIX}AudioTranscribe"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
TRANSCRIBER = "assemblyai/universal-3-5-pro"
TRIAGE_TEXTS = WORKFLOW_TEXTS["audio-01-triage-a-voicemail"]
DUB_TEXTS = WORKFLOW_TEXTS["audio-02-dub-a-clip"]

TRANSCRIBE_VOICEMAIL = Subgraph(
    name=SHARED_TEXTS["transcribe"],
    nodes=(
        Node("transcribe", TRANSCRIBE, {"model": TRANSCRIBER}, is_paid=True),
        Node("save", SAVE_TEXT, {"filename_prefix": "voicemail/transcript"}),
    ),
    links=(("transcribe.text", "save.text"),),
    columns=(("transcribe",), ("save",)),
    inputs=(("audio", "transcribe.audio"),),
    outputs=(("text", "transcribe.text"),),
    description=TRIAGE_TEXTS["transcribe_description"],
)

TRIAGE = Subgraph(
    name=SHARED_TEXTS["triage"],
    nodes=(
        Node("decide", DECIDE, is_paid=True),
        Node("department", READ, {"question": "department"}),
    ),
    links=(("decide.answers", "department.answers"),),
    columns=(("decide",), ("department",)),
    inputs=(("text", "decide.situation"), ("questions", "decide.questions")),
    outputs=(("department", "department.answer"), ("summary", "decide.summary")),
    description=TRIAGE_TEXTS["triage_description"],
)

REPLY = Subgraph(
    name=SHARED_TEXTS["reply"],
    nodes=(
        Node(
            "request",
            FORMAT,
            {
                "f_string": (
                    "You work in the {b} team. Write what you say when you call this customer back: under 60 words, "
                    "friendly, and answering what they asked.\n\nTheir voicemail:\n{a}"
                )
            },
        ),
        Node("script", ASK, {"model": "openai/gpt-6-luna"}, is_paid=True),
        Node("speak", SPEAK, {"model": "google/gemini-3.8-flash-tts", "model.voice": "Kore"}, is_paid=True),
        Node("save", SAVE_AUDIO, {"filename_prefix": "voicemail/reply"}),
    ),
    links=(
        ("request.STRING", "script.prompt"),
        ("script.text", "speak.text"),
        ("speak.audio", "save.audio"),
    ),
    columns=(("request",), ("script",), ("speak", "save")),
    inputs=(("text", "request.values.a"), ("department", "request.values.b")),
    description=TRIAGE_TEXTS["reply_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

TRIAGE_VOICEMAIL = Workflow(
    slug="audio-01-triage-a-voicemail",
    nodes=(
        Node("voicemail", AUDIO, {"audio": ""}),
        Node("transcribe", TRANSCRIBE_VOICEMAIL.name),
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
        ),
        Node(
            "callback",
            QUESTION,
            {"name": "callback", "instructions": "Does the caller ask to be called back?"},
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
        ),
        Node("triage", TRIAGE.name),
        Node("summary", PREVIEW, title=SHARED_TEXTS["summary"]),
        Node("reply", REPLY.name),
    ),
    links=(
        ("voicemail.AUDIO", "transcribe.audio"),
        ("department.questions", "callback.questions"),
        ("callback.questions", "urgency.questions"),
        ("transcribe.text", "triage.text"),
        ("urgency.questions", "triage.questions"),
        ("triage.summary", "summary.source"),
        ("transcribe.text", "reply.text"),
        ("triage.department", "reply.department"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("voicemail",),), note=TRIAGE_TEXTS["input"]),),
        (Group(SHARED_TEXTS["transcribe"], (("transcribe",),), STAGE_COLOUR, TRIAGE_TEXTS["transcribe"]),),
        (
            Group(
                SHARED_TEXTS["triage"],
                (("department", "callback", "urgency"), ("triage", "summary")),
                STAGE_COLOUR,
                TRIAGE_TEXTS["triage"],
            ),
        ),
        (Group(SHARED_TEXTS["reply"], (("reply",),), STAGE_COLOUR, TRIAGE_TEXTS["reply"]),),
    ),
    subgraphs=(TRANSCRIBE_VOICEMAIL, TRIAGE, REPLY),
)

TRANSCRIBE_CLIP = Subgraph(
    name=SHARED_TEXTS["transcribe"],
    nodes=(
        Node("transcribe", TRANSCRIBE, {"model": TRANSCRIBER, "timestamps": "segments"}, is_paid=True),
        Node("save", SAVE_TEXT, {"filename_prefix": "dub/subtitles"}),
    ),
    links=(("transcribe.subtitles", "save.text"),),
    columns=(("transcribe",), ("save",)),
    inputs=(("audio", "transcribe.audio"),),
    outputs=(("text", "transcribe.text"),),
    description=DUB_TEXTS["transcribe_description"],
)

TRANSLATE = Subgraph(
    name=SHARED_TEXTS["translate"],
    nodes=(
        Node("language", TEXT, {"value": "Spanish"}, title=SHARED_TEXTS["language"]),
        Node(
            "request",
            FORMAT,
            {
                "f_string": (
                    "Translate this text into natural {a}. Keep the meaning and the tone, and answer with the "
                    "translation only.\n\n{b}"
                )
            },
        ),
        Node("translate", ASK, {"model": "openai/gpt-6-sol"}, is_paid=True),
        Node("situation", FORMAT, {"f_string": "Original:\n{a}\n\n{b} translation:\n{c}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("accurate", READ, {"question": "accurate"}),
    ),
    links=(
        ("language.STRING", "request.values.a"),
        ("request.STRING", "translate.prompt"),
        ("language.STRING", "situation.values.b"),
        ("translate.text", "situation.values.c"),
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "accurate.answers"),
    ),
    columns=(("language", "request"), ("translate",), ("situation", "decide", "accurate")),
    inputs=(
        ("text", "request.values.b"),
        ("text", "situation.values.a"),
        ("questions", "decide.questions"),
        ("language", "language.value"),
    ),
    outputs=(
        ("translation", "translate.text"),
        ("accurate", "accurate.is_yes"),
        ("summary", "decide.summary"),
    ),
    description=DUB_TEXTS["translate_description"],
)

SPEAK_DUB = Subgraph(
    name=SHARED_TEXTS["speak"],
    nodes=(
        Node("speak", SPEAK, {"model": "fish-audio/s2.1-pro"}, is_paid=True),
        Node("approved", TEXT, {"value": "dub/approved"}, title=SHARED_TEXTS["approved"]),
        Node("review", TEXT, {"value": "dub/review"}, title=SHARED_TEXTS["review"]),
        Node("folder", SWITCH),
        Node("save", SAVE_AUDIO),
    ),
    links=(
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("speak.audio", "save.audio"),
    ),
    columns=(("speak",), ("approved", "review", "folder"), ("save",)),
    inputs=(
        ("translation", "speak.text"),
        ("audio", "speak.voice_sample"),
        ("text", "speak.sample_transcript"),
        ("accurate", "folder.switch"),
        ("approved", "approved.value"),
        ("review", "review.value"),
    ),
    description=DUB_TEXTS["speak_description"],
    previews=(("save", AUDIO_PREVIEW),),
)

DUB_CLIP = Workflow(
    slug="audio-02-dub-a-clip",
    nodes=(
        Node("clip", AUDIO, {"audio": ""}),
        Node("transcribe", TRANSCRIBE_CLIP.name),
        Node(
            "accurate",
            QUESTION,
            {
                "name": "accurate",
                "instructions": "Does the translation say the same as the original, with nothing added or left out?",
            },
        ),
        Node("translate", TRANSLATE.name),
        Node("summary", PREVIEW, title=SHARED_TEXTS["summary"]),
        Node("speak", SPEAK_DUB.name),
    ),
    links=(
        ("clip.AUDIO", "transcribe.audio"),
        ("transcribe.text", "translate.text"),
        ("accurate.questions", "translate.questions"),
        ("translate.summary", "summary.source"),
        ("translate.translation", "speak.translation"),
        ("clip.AUDIO", "speak.audio"),
        ("transcribe.text", "speak.text"),
        ("translate.accurate", "speak.accurate"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("clip",),), note=DUB_TEXTS["input"]),),
        (Group(SHARED_TEXTS["transcribe"], (("transcribe",),), STAGE_COLOUR, DUB_TEXTS["transcribe"]),),
        (
            Group(
                SHARED_TEXTS["translate"],
                (("accurate",), ("translate", "summary")),
                STAGE_COLOUR,
                DUB_TEXTS["translate"],
            ),
        ),
        (Group(SHARED_TEXTS["speak"], (("speak",),), STAGE_COLOUR, DUB_TEXTS["speak"]),),
    ),
    subgraphs=(TRANSCRIBE_CLIP, TRANSLATE, SPEAK_DUB),
)

AUDIO_WORKFLOWS = (TRIAGE_VOICEMAIL, DUB_CLIP)

__all__ = ["AUDIO_WORKFLOWS"]

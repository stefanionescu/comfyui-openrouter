"""The image workflows: Jev picks the best image for an occasion and rejects distorted drafts."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.descriptions.notes import WORKFLOW_TEXTS
from scripts.workflows.page.config import STAGE_COLOUR, IMAGE_PREVIEW
from scripts.workflows.page.graph import Node, Group, Subgraph, Workflow
from scripts.config import (
    TEXT,
    BATCH,
    FORMAT,
    SWITCH,
    PREVIEW,
    FROM_BATCH,
    SAVE_IMAGE,
    TEXT_BLOCK,
)

ASK = f"{NODE_PREFIX}ChatAsk"
GENERATE = f"{NODE_PREFIX}ImageGenerate"
EMBED = f"{NODE_PREFIX}SearchEmbed"
DECIDE = f"{NODE_PREFIX}DecisionAsk"
QUESTION = f"{NODE_PREFIX}DecisionAddQuestion"
READ = f"{NODE_PREFIX}DecisionReadAnswer"
READER = "openai/gpt-6-luna"
GPT_IMAGE = "openai/gpt-image-2.5-flare"
EMBEDDER = "google/gemini-embedding-2"
OCCASION_TEXTS = WORKFLOW_TEXTS["image-01-pick-the-best-image-for-an-occasion"]
DRAFT_TEXTS = WORKFLOW_TEXTS["image-02-reject-distorted-images"]

DRAW = Subgraph(
    name=SHARED_TEXTS["draw"],
    nodes=(
        Node(
            "first",
            GENERATE,
            {"model": GPT_IMAGE, "aspect_ratio": "1:1", "quality": "medium"},
            is_paid=True,
        ),
        Node("second", GENERATE, {"model": "microsoft/mai-image-2.6-flash", "aspect_ratio": "1:1"}, is_paid=True),
        Node("third", GENERATE, {"model": "recraft/recraft-v4.1-flash", "aspect_ratio": "1:1"}, is_paid=True),
        Node("batch", BATCH),
        Node(
            "describe",
            ASK,
            {
                "model": READER,
                "prompt": (
                    "Describe each image in two sentences, as candidate_1, candidate_2, and candidate_3 in the "
                    "order given. Mention any visible flaw, such as warped shapes or stray lettering."
                ),
            },
            is_paid=True,
        ),
    ),
    links=(
        ("first.images", "batch.images.image0"),
        ("second.images", "batch.images.image1"),
        ("third.images", "batch.images.image2"),
        ("first.images", "describe.images.image_1"),
        ("second.images", "describe.images.image_2"),
        ("third.images", "describe.images.image_3"),
    ),
    columns=(("first", "second", "third"), ("batch", "describe")),
    inputs=(("brief", "first.prompt"), ("brief", "second.prompt"), ("brief", "third.prompt")),
    outputs=(("images", "batch.IMAGE"), ("descriptions", "describe.text")),
    description=OCCASION_TEXTS["draw_description"],
)

CHOOSE = Subgraph(
    name=SHARED_TEXTS["choose"],
    nodes=(
        Node("situation", FORMAT, {"f_string": "Brief:\n{a}\n\nCandidates:\n{b}"}),
        Node("decide", DECIDE, is_paid=True),
        Node("best", READ, {"question": "best"}),
        Node("ready", READ, {"question": "ready"}),
        Node("chosen", FROM_BATCH),
        Node("approved", TEXT, {"value": "occasion/approved"}, title=SHARED_TEXTS["approved"]),
        Node("review", TEXT, {"value": "occasion/review"}, title=SHARED_TEXTS["review"]),
        Node("folder", SWITCH),
        Node("save", SAVE_IMAGE),
    ),
    links=(
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "best.answers"),
        ("decide.answers", "ready.answers"),
        ("best.level", "chosen.batch_index"),
        ("ready.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("chosen.IMAGE", "save.images"),
    ),
    columns=(("situation", "decide"), ("best", "ready", "chosen"), ("approved", "review", "folder"), ("save",)),
    inputs=(
        ("brief", "situation.values.a"),
        ("descriptions", "situation.values.b"),
        ("images", "chosen.image"),
        ("questions", "decide.questions"),
        ("approved", "approved.value"),
        ("review", "review.value"),
    ),
    outputs=(("summary", "decide.summary"),),
    description=OCCASION_TEXTS["choose_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

PICK_OCCASION_IMAGE = Workflow(
    slug="image-01-pick-the-best-image-for-an-occasion",
    nodes=(
        Node(
            "brief",
            TEXT_BLOCK,
            {
                "value": (
                    "Cover image for a six-year-old's dinosaur birthday party invitation. Bright and friendly, "
                    "one cartoon dinosaur with a party hat, plenty of empty space for text, no lettering."
                )
            },
            title=SHARED_TEXTS["brief"],
        ),
        Node("draw", DRAW.name),
        Node(
            "best",
            QUESTION,
            {
                "name": "best",
                "instructions": "Which candidate suits the occasion best?",
                "answer_type": "one choice",
                "answer_type.options": "candidate_1\ncandidate_2\ncandidate_3",
            },
        ),
        Node(
            "ready",
            QUESTION,
            {
                "name": "ready",
                "instructions": (
                    "Is the best of the three candidates ready to send to the client as it is, with no visible flaw?"
                ),
            },
        ),
        Node("choose", CHOOSE.name),
        Node("summary", PREVIEW, title=SHARED_TEXTS["summary"]),
    ),
    links=(
        ("brief.STRING", "draw.brief"),
        ("brief.STRING", "choose.brief"),
        ("draw.images", "choose.images"),
        ("draw.descriptions", "choose.descriptions"),
        ("best.questions", "ready.questions"),
        ("ready.questions", "choose.questions"),
        ("choose.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief",),), note=OCCASION_TEXTS["input"]),),
        (Group(SHARED_TEXTS["draw"], (("draw",),), STAGE_COLOUR, OCCASION_TEXTS["draw"]),),
        (
            Group(
                SHARED_TEXTS["choose"],
                (("best", "ready"), ("choose", "summary")),
                STAGE_COLOUR,
                OCCASION_TEXTS["choose"],
            ),
        ),
    ),
    subgraphs=(DRAW, CHOOSE),
)

INSPECT = Subgraph(
    name=SHARED_TEXTS["inspect"],
    nodes=(
        Node(
            "description",
            FORMAT,
            {"f_string": "A clean, sharp, undistorted photo of {a}, with natural hands, faces, and objects"},
        ),
        Node("clean", EMBED, {"model": EMBEDDER}, title=SHARED_TEXTS["clean"], is_paid=True),
        Node(
            "distorted",
            EMBED,
            {
                "model": EMBEDDER,
                "texts": (
                    "A distorted AI image with warped hands, extra fingers, melted faces, broken objects, "
                    "and garbled text"
                ),
            },
            title=SHARED_TEXTS["distorted"],
            is_paid=True,
        ),
        Node(
            "defects",
            ASK,
            {
                "model": READER,
                "prompt": (
                    "List every visible defect in this image: extra or missing fingers, warped faces or limbs, "
                    "broken objects, impossible geometry, or garbled text. Answer none if there are none."
                ),
            },
            is_paid=True,
        ),
    ),
    links=(("description.STRING", "clean.texts"),),
    columns=(("description", "clean"), ("distorted",), ("defects",)),
    inputs=(
        ("subject", "description.values.a"),
        ("image", "clean.images.image_1"),
        ("image", "distorted.images.image_1"),
        ("image", "defects.images.image_1"),
    ),
    outputs=(("clean", "clean.similarities"), ("distorted", "distorted.similarities"), ("defects", "defects.text")),
    description=DRAFT_TEXTS["inspect_description"],
)

CHECK_DRAFT = Subgraph(
    name=SHARED_TEXTS["check"],
    nodes=(
        Node(
            "situation",
            FORMAT,
            {
                "f_string": (
                    "Subject: {a}\n\nImage embedding similarity, as [description, draft], to a clean description: "
                    "{b}\nTo a distorted description: {c}\n\nDefects a vision model saw: {d}"
                )
            },
        ),
        Node("decide", DECIDE, is_paid=True),
        Node("read", READ, {"question": "distorted"}),
        Node("rejected", TEXT, {"value": "drafts/rejected"}, title=SHARED_TEXTS["rejected"]),
        Node("approved", TEXT, {"value": "drafts/approved"}, title=SHARED_TEXTS["approved"]),
        Node("folder", SWITCH),
        Node("save", SAVE_IMAGE),
    ),
    links=(
        ("situation.STRING", "decide.situation"),
        ("decide.answers", "read.answers"),
        ("read.is_yes", "folder.switch"),
        ("rejected.STRING", "folder.on_true"),
        ("approved.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
    ),
    columns=(("situation", "decide"), ("read", "rejected", "approved"), ("folder", "save")),
    inputs=(
        ("subject", "situation.values.a"),
        ("clean", "situation.values.b"),
        ("distorted", "situation.values.c"),
        ("defects", "situation.values.d"),
        ("image", "save.images"),
        ("questions", "decide.questions"),
        ("approved", "approved.value"),
        ("rejected", "rejected.value"),
    ),
    outputs=(("summary", "decide.summary"),),
    description=DRAFT_TEXTS["check_description"],
    previews=(("save", IMAGE_PREVIEW),),
)

REJECT_DISTORTED = Workflow(
    slug="image-02-reject-distorted-images",
    nodes=(
        Node(
            "subject",
            TEXT_BLOCK,
            {"value": "A violinist playing on a city rooftop at sunset, both hands and the bow clearly visible"},
            title=SHARED_TEXTS["subject"],
        ),
        Node(
            "draft",
            GENERATE,
            {"model": "microsoft/mai-image-2.6-flash", "aspect_ratio": "4:3"},
            is_paid=True,
        ),
        Node("inspect", INSPECT.name),
        Node(
            "distorted",
            QUESTION,
            {
                "name": "distorted",
                "instructions": "Is the draft distorted, with defects a viewer would notice?",
                "answer_type.yes_means": "Warped anatomy, extra or missing parts, broken objects, or garbled text.",
                "answer_type.no_means": "The picture looks correct and matches the subject.",
            },
        ),
        Node("check", CHECK_DRAFT.name),
        Node("summary", PREVIEW, title=SHARED_TEXTS["summary"]),
    ),
    links=(
        ("subject.STRING", "draft.prompt"),
        ("subject.STRING", "inspect.subject"),
        ("draft.images", "inspect.image"),
        ("subject.STRING", "check.subject"),
        ("inspect.clean", "check.clean"),
        ("inspect.distorted", "check.distorted"),
        ("inspect.defects", "check.defects"),
        ("draft.images", "check.image"),
        ("distorted.questions", "check.questions"),
        ("check.summary", "summary.source"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("subject",),), note=DRAFT_TEXTS["input"]),),
        (Group(SHARED_TEXTS["draw"], (("draft",),), STAGE_COLOUR, DRAFT_TEXTS["draw"]),),
        (Group(SHARED_TEXTS["inspect"], (("inspect",),), STAGE_COLOUR, DRAFT_TEXTS["inspect"]),),
        (Group(SHARED_TEXTS["check"], (("distorted",), ("check", "summary")), STAGE_COLOUR, DRAFT_TEXTS["check"]),),
    ),
    subgraphs=(INSPECT, CHECK_DRAFT),
)

IMAGE_WORKFLOWS = (PICK_OCCASION_IMAGE, REJECT_DISTORTED)

__all__ = ["IMAGE_WORKFLOWS"]

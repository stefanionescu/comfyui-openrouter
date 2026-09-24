"""The image workflows: Jev picks the best image for an occasion and rejects distorted drafts."""

from __future__ import annotations

from src.config.namespace import NODE_PREFIX
from scripts.workflows.page.config import STAGE_COLOUR
from scripts.workflows.descriptions.texts import SHARED_TEXTS
from scripts.workflows.page.graph import Node, Group, Workflow
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
WRITER = "openai/gpt-6-sol"
GPT_IMAGE = "openai/gpt-image-2.5-flare"


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
            title="Occasion Brief",
        ),
        Node(
            "best",
            QUESTION,
            {
                "name": "best",
                "instructions": "Which candidate suits the occasion best?",
                "answer_type": "one choice",
                "answer_type.options": "candidate_1\ncandidate_2\ncandidate_3",
            },
            title="Best Candidate",
        ),
        Node(
            "ready",
            QUESTION,
            {
                "name": "ready",
                "instructions": "Can the chosen candidate go to the client as it is, with no visible flaws?",
            },
            title="Ready to Send",
        ),
        Node(
            "first",
            GENERATE,
            {"model": GPT_IMAGE, "model.aspect_ratio": "1:1", "model.quality": "medium"},
            title="Candidate 1 (GPT Image 2.5)",
            is_paid=True,
        ),
        Node(
            "second",
            GENERATE,
            {"model": "microsoft/mai-image-2.6-flash", "model.aspect_ratio": "1:1"},
            title="Candidate 2 (MAI Image 2.6)",
            is_paid=True,
        ),
        Node(
            "third",
            GENERATE,
            {"model": "recraft/recraft-v4.1-flash", "model.aspect_ratio": "1:1"},
            title="Candidate 3 (Recraft V4.1)",
            is_paid=True,
        ),
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
            title="Describe the Candidates",
            is_paid=True,
        ),
        Node("situation", FORMAT, {"f_string": "Brief:\n{a}\n\nCandidates:\n{b}"}, title="Brief and Candidates"),
        Node("decide", DECIDE, title="Choose a Candidate", is_paid=True),
        Node("read_best", READ, {"question": "best"}, title="Read Best"),
        Node("read_ready", READ, {"question": "ready"}, title="Read Ready"),
        Node("batch", BATCH, title="All Candidates"),
        Node("chosen", FROM_BATCH, title="Chosen Image"),
        Node("approved", TEXT, {"value": "occasion/approved"}, title="Approved Folder"),
        Node("review", TEXT, {"value": "occasion/review"}, title="Review Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_IMAGE, title="Save the Chosen Image"),
        Node("summary", PREVIEW, title="Decision Summary"),
    ),
    links=(
        ("brief.STRING", "first.prompt"),
        ("brief.STRING", "second.prompt"),
        ("brief.STRING", "third.prompt"),
        ("brief.STRING", "situation.values.a"),
        ("first.images", "describe.model.images.image_1"),
        ("second.images", "describe.model.images.image_2"),
        ("third.images", "describe.model.images.image_3"),
        ("describe.text", "situation.values.b"),
        ("situation.STRING", "decide.situation"),
        ("best.questions", "ready.questions"),
        ("ready.questions", "decide.questions"),
        ("decide.answers", "read_best.answers"),
        ("decide.answers", "read_ready.answers"),
        ("decide.summary", "summary.source"),
        ("first.images", "batch.images.image0"),
        ("second.images", "batch.images.image1"),
        ("third.images", "batch.images.image2"),
        ("batch.IMAGE", "chosen.image"),
        ("read_best.level", "chosen.batch_index"),
        ("read_ready.is_yes", "folder.switch"),
        ("approved.STRING", "folder.on_true"),
        ("review.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("chosen.IMAGE", "save.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("brief",), ("best", "ready"))),),
        (Group(SHARED_TEXTS["candidates"], (("first", "second", "third"),), STAGE_COLOUR),),
        (
            Group(
                SHARED_TEXTS["choose"], (("describe", "situation"), ("decide", "read_best", "read_ready")), STAGE_COLOUR
            ),
        ),
        (Group(SHARED_TEXTS["save"], (("batch", "chosen", "approved", "review", "folder"), ("save", "summary"))),),
    ),
)

REJECT_DISTORTED = Workflow(
    slug="image-02-reject-distorted-images",
    nodes=(
        Node(
            "subject",
            TEXT_BLOCK,
            {"value": "A violinist playing on a city rooftop at sunset, both hands and the bow clearly visible"},
            title="Subject",
        ),
        Node(
            "distorted",
            QUESTION,
            {
                "name": "distorted",
                "instructions": "Is the draft distorted, with defects a viewer would notice?",
                "answer_type.yes_means": "Warped anatomy, extra or missing parts, broken objects, or garbled text.",
                "answer_type.no_means": "The picture looks correct and matches the subject.",
            },
            title="Distorted",
        ),
        Node(
            "draft",
            GENERATE,
            {"model": "microsoft/mai-image-2.6-flash", "model.aspect_ratio": "4:3"},
            title="Draft",
            is_paid=True,
        ),
        Node(
            "clean_text",
            FORMAT,
            {"f_string": "A clean, sharp, undistorted photo of {a}, with natural hands, faces, and objects"},
            title="Clean Description",
        ),
        Node(
            "clean",
            EMBED,
            {"model": "google/gemini-embedding-2"},
            title="Match a Clean Picture",
            is_paid=True,
        ),
        Node(
            "broken",
            EMBED,
            {
                "model": "google/gemini-embedding-2",
                "texts": (
                    "A distorted AI image with warped hands, extra fingers, melted faces, broken objects, "
                    "and garbled text"
                ),
            },
            title="Match a Distorted Picture",
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
            title="Find Defects",
            is_paid=True,
        ),
        Node(
            "situation",
            FORMAT,
            {
                "f_string": (
                    "Subject: {a}\n\nImage embedding similarity, as [description, draft], to a clean description: "
                    "{b}\nTo a distorted description: {c}\n\nDefects a vision model saw: {d}"
                )
            },
            title="All the Signals",
        ),
        Node("decide", DECIDE, title="Check the Draft", is_paid=True),
        Node("read", READ, {"question": "distorted"}, title="Read Distorted"),
        Node("rejected", TEXT, {"value": "drafts/rejected"}, title="Rejected Folder"),
        Node("approved", TEXT, {"value": "drafts/approved"}, title="Approved Folder"),
        Node("folder", SWITCH, title="Choose the Folder"),
        Node("save", SAVE_IMAGE, title="Save the Draft"),
        Node("summary", PREVIEW, title="Decision Summary"),
    ),
    links=(
        ("subject.STRING", "draft.prompt"),
        ("subject.STRING", "clean_text.values.a"),
        ("subject.STRING", "situation.values.a"),
        ("clean_text.STRING", "clean.texts"),
        ("draft.images", "clean.model.images.image_1"),
        ("draft.images", "broken.model.images.image_1"),
        ("draft.images", "defects.model.images.image_1"),
        ("clean.similarities", "situation.values.b"),
        ("broken.similarities", "situation.values.c"),
        ("defects.text", "situation.values.d"),
        ("situation.STRING", "decide.situation"),
        ("distorted.questions", "decide.questions"),
        ("decide.answers", "read.answers"),
        ("decide.summary", "summary.source"),
        ("read.is_yes", "folder.switch"),
        ("rejected.STRING", "folder.on_true"),
        ("approved.STRING", "folder.on_false"),
        ("folder.output", "save.filename_prefix"),
        ("draft.images", "save.images"),
    ),
    stacks=(
        (Group(SHARED_TEXTS["input"], (("subject", "distorted"),)),),
        (Group(SHARED_TEXTS["draft"], (("draft", "clean_text"),), STAGE_COLOUR),),
        (
            Group(
                SHARED_TEXTS["check"], (("clean", "broken"), ("defects", "situation"), ("decide", "read")), STAGE_COLOUR
            ),
        ),
        (Group(SHARED_TEXTS["save"], (("rejected", "approved", "folder"), ("save", "summary"))),),
    ),
)

IMAGE_WORKFLOWS = (PICK_OCCASION_IMAGE, REJECT_DISTORTED)

__all__ = ["IMAGE_WORKFLOWS"]

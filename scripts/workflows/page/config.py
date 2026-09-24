"""The workflow page: distances, colours, node sizes and subgraph numbering."""

from scripts.config import (
    AUDIO,
    IMAGE,
    PREVIEW,
    SAVE_TEXT,
    SAVE_AUDIO,
    SAVE_IMAGE,
    SAVE_VIDEO,
    PREVIEW_AUDIO,
    PREVIEW_IMAGE,
)

# Page layout: distances in page pixels.
GUTTER = 30
# Space between nodes inside a group.
NODE_GAP = 40
# Space under a node when another sits below it: the lower node's title bar and its source badge draw above it.
STACK_GAP = 64
GROUP_TOP = 110
CANVAS_ORIGIN = (0, 30)
INNER_ORIGIN = (200, 140)
PORT_WIDTH = 120
# Group colours: inputs and controls, and generation stages.
INPUT_COLOUR = "#55746b"
STAGE_COLOUR = "#68688c"
# Nodes that send paid requests are drawn in these colours.
PAID_COLOURS = {"color": "#432", "bgcolor": "#653"}
# The page mode of a bypassed node: it passes its inputs through and runs nothing.
BYPASS_MODE = 4
# Node IDs are one space across a workflow, so each subgraph numbers its nodes from its own hundred.
SUBGRAPH_ID_STEP = 100
# Node width and the heights ComfyUI's page adds up for a node, checked on frontend 1.49.6: a row per socket,
# each widget and the gap after it, the space under the widgets, and the space under the node.
NODE_WIDTH = 340
SLOT_HEIGHT = 20
WIDGET_HEIGHT = 20
WIDGET_GAP = 4
WIDGETS_PADDING = 8
NODE_PADDING = 6
# A multi-line text and a multi-select list are drawn at least this tall.
MULTILINE_HEIGHT = 50
MULTISELECT_HEIGHT = 62
# The notes, measured on frontend 1.49.6: their width, the frame around their text, the smallest height the
# page draws, one wrapped line, the space a blank line leaves between paragraphs, and the characters per line.
NOTE_WIDTH = 620
NOTE_PADDING = 26
NOTE_MIN_HEIGHT = 88
NOTE_LINE_HEIGHT = 12
NOTE_PARAGRAPH_GAP = 10
NOTE_CHARS_PER_LINE = 126
# A dropdown whose options add controls, a row of sockets that grows by one as its last socket is linked,
# and the input types the page draws as widgets.
DROPDOWN_TYPE = "COMFY_DYNAMICCOMBO_V3"
AUTOGROW_TYPE = "COMFY_AUTOGROW_V3"
WIDGET_TYPES = frozenset({"INT", "FLOAT", "STRING", "BOOLEAN", "COMBO", DROPDOWN_TYPE})
# Nodes that draw their own panel, measured in the page. The save nodes are sized for their empty state;
# ComfyUI grows them as their viewers fill.
DOM_SIZES: dict[str, tuple[int, int]] = {
    IMAGE: (340, 350),
    AUDIO: (340, 136),
    PREVIEW: (340, 240),
    SAVE_TEXT: (340, 170),
    SAVE_IMAGE: (340, 290),
    PREVIEW_IMAGE: (340, 290),
    PREVIEW_AUDIO: (340, 150),
    SAVE_AUDIO: (340, 136),
    SAVE_VIDEO: (340, 106),
}

__all__ = [
    "AUTOGROW_TYPE",
    "BYPASS_MODE",
    "CANVAS_ORIGIN",
    "DOM_SIZES",
    "DROPDOWN_TYPE",
    "GROUP_TOP",
    "GUTTER",
    "INNER_ORIGIN",
    "INPUT_COLOUR",
    "MULTILINE_HEIGHT",
    "MULTISELECT_HEIGHT",
    "NODE_GAP",
    "NODE_PADDING",
    "NODE_WIDTH",
    "NOTE_CHARS_PER_LINE",
    "NOTE_LINE_HEIGHT",
    "NOTE_MIN_HEIGHT",
    "NOTE_PADDING",
    "NOTE_PARAGRAPH_GAP",
    "NOTE_WIDTH",
    "PAID_COLOURS",
    "PORT_WIDTH",
    "SLOT_HEIGHT",
    "STACK_GAP",
    "STAGE_COLOUR",
    "SUBGRAPH_ID_STEP",
    "WIDGETS_PADDING",
    "WIDGET_GAP",
    "WIDGET_HEIGHT",
    "WIDGET_TYPES",
]

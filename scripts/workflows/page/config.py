"""The workflow page: distances, colours, node sizes and subgraph numbering."""

from scripts.config import AUDIO, IMAGE, PREVIEW, SAVE_TEXT, SAVE_AUDIO, SAVE_IMAGE, SAVE_VIDEO, PREVIEW_AUDIO

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
# Group colours: inputs and controls, generation stages, and saving.
INPUT_COLOUR = "#55746b"
STAGE_COLOUR = "#68688c"
SAVE_COLOUR = "#946e4b"
# Nodes that send paid requests are drawn in these colours.
PAID_COLOURS = {"color": "#432", "bgcolor": "#653"}
# The page mode of a bypassed node: it passes its inputs through and runs nothing.
BYPASS_MODE = 4
# Node IDs are one space across a workflow, so each subgraph numbers its nodes from its own hundred.
SUBGRAPH_ID_STEP = 100
# Node width, and the height of a title, a socket row and a widget row, in page pixels.
NODE_WIDTH = 340
TITLE_HEIGHT = 6
SLOT_HEIGHT = 20
WIDGET_HEIGHT = 32
# A child widget of a dynamic dropdown, a multi-line text and a multi-select list take these heights.
CHILD_WIDGET_HEIGHT = 28
MULTILINE_HEIGHT = 82
MULTISELECT_HEIGHT = 62
# The Start Here note: its width, the rows its title and padding take, one wrapped line and the characters per line.
NOTE_WIDTH = 620
NOTE_PADDING = 56
NOTE_LINE_HEIGHT = 12
NOTE_CHARS_PER_LINE = 115
# A row of sockets that grows by one as its last socket is linked.
AUTOGROW_TYPE = "COMFY_AUTOGROW_V3"
# Nodes that draw their own panel, measured in the page. The save nodes are sized for their empty state;
# ComfyUI grows them as their viewers fill.
DOM_SIZES: dict[str, tuple[int, int]] = {
    IMAGE: (340, 350),
    AUDIO: (340, 136),
    PREVIEW: (340, 240),
    SAVE_TEXT: (340, 170),
    SAVE_IMAGE: (340, 290),
    PREVIEW_AUDIO: (340, 150),
    SAVE_AUDIO: (340, 250),
    SAVE_VIDEO: (340, 290),
}

__all__ = [
    "AUTOGROW_TYPE",
    "BYPASS_MODE",
    "CANVAS_ORIGIN",
    "CHILD_WIDGET_HEIGHT",
    "DOM_SIZES",
    "GROUP_TOP",
    "GUTTER",
    "INNER_ORIGIN",
    "INPUT_COLOUR",
    "MULTILINE_HEIGHT",
    "MULTISELECT_HEIGHT",
    "NODE_GAP",
    "NODE_WIDTH",
    "NOTE_CHARS_PER_LINE",
    "NOTE_LINE_HEIGHT",
    "NOTE_PADDING",
    "NOTE_WIDTH",
    "PAID_COLOURS",
    "PORT_WIDTH",
    "SAVE_COLOUR",
    "SLOT_HEIGHT",
    "STACK_GAP",
    "STAGE_COLOUR",
    "SUBGRAPH_ID_STEP",
    "TITLE_HEIGHT",
    "WIDGET_HEIGHT",
]

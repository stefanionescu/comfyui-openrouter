"""The workflow page: distances, colours, node sizes and subgraph numbering."""

from scripts.nodes.host import HostNode

# The note node the page draws each group's text in.
NOTE = "MarkdownNote"
# The previews a save node draws, which a placed subgraph can show: an image, an audio player, and a text.
IMAGE_PREVIEW = "$$canvas-image-preview"
AUDIO_PREVIEW = "audioUI"
TEXT_PREVIEW = "preview_text"
# Page layout: distances in page pixels.
GUTTER = 30
# Space between nodes inside a group.
NODE_GAP = 40
# Space under a node when another sits below it: the lower node's title bar and its source badge draw above it.
STACK_GAP = 64
GROUP_TOP = 110
CANVAS_ORIGIN = (0, 30)
INNER_ORIGIN = (200, 140)
# A subgraph's input and output ports: their width, and the room their links take to reach the nodes.
PORT_WIDTH = 120
PORT_GAP = 90
# Group colours: inputs and controls, and generation stages.
INPUT_COLOUR = "#55746b"
STAGE_COLOUR = "#68688c"
# Nodes that send paid requests are drawn in these colours.
PAID_COLOURS = {"color": "#432", "bgcolor": "#653"}
# The page mode of a bypassed node.
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
# The notes, measured on frontend 1.49.6: the frame around their text, the smallest height the page draws,
# one wrapped line, the space a blank line leaves between paragraphs, the width the text loses to the frame and
# to a numbered list's indent, and the width of one character and of one code character, rounded up so a line
# wraps no later than the page wraps it.
NOTE_PADDING = 26
NOTE_MIN_HEIGHT = 88
NOTE_LINE_HEIGHT = 12
NOTE_PARAGRAPH_GAP = 10
NOTE_SIDE_PADDING = 20
NOTE_LIST_INDENT = 40
NOTE_CHARACTER_WIDTH = 5
NOTE_CODE_CHARACTER_WIDTH = 7
# A dropdown whose options add widgets, and a row of sockets that grows by one as its last socket is linked.
DROPDOWN_TYPE = "COMFY_DYNAMICCOMBO_V3"
AUTOGROW_TYPE = "COMFY_AUTOGROW_V3"
# A switch's sockets, which take the type of the values linked into them, and a socket that takes any type,
# such as Format Text's.
MATCH_TYPE = "COMFY_MATCHTYPE_V3"
ANY_TYPE = "*"
# Nodes that draw their own panel, measured in the page. The save nodes are sized for their empty state;
# ComfyUI grows them as their viewers fill.
DOM_SIZES: dict[str, tuple[int, int]] = {
    HostNode.IMAGE: (340, 350),
    HostNode.AUDIO: (340, 136),
    HostNode.PREVIEW: (340, 240),
    HostNode.SAVE_TEXT: (340, 170),
    HostNode.SAVE_IMAGE: (340, 290),
    HostNode.PREVIEW_IMAGE: (340, 290),
    HostNode.PREVIEW_AUDIO: (340, 150),
    HostNode.SAVE_AUDIO: (340, 136),
    HostNode.SAVE_VIDEO: (340, 106),
}

__all__ = [
    "ANY_TYPE",
    "AUDIO_PREVIEW",
    "AUTOGROW_TYPE",
    "BYPASS_MODE",
    "CANVAS_ORIGIN",
    "DOM_SIZES",
    "DROPDOWN_TYPE",
    "GROUP_TOP",
    "GUTTER",
    "IMAGE_PREVIEW",
    "INNER_ORIGIN",
    "INPUT_COLOUR",
    "MATCH_TYPE",
    "MULTILINE_HEIGHT",
    "MULTISELECT_HEIGHT",
    "NODE_GAP",
    "NODE_PADDING",
    "NODE_WIDTH",
    "NOTE",
    "NOTE_CHARACTER_WIDTH",
    "NOTE_CODE_CHARACTER_WIDTH",
    "NOTE_LINE_HEIGHT",
    "NOTE_LIST_INDENT",
    "NOTE_MIN_HEIGHT",
    "NOTE_PADDING",
    "NOTE_PARAGRAPH_GAP",
    "NOTE_SIDE_PADDING",
    "PAID_COLOURS",
    "PORT_GAP",
    "PORT_WIDTH",
    "SLOT_HEIGHT",
    "STACK_GAP",
    "STAGE_COLOUR",
    "SUBGRAPH_ID_STEP",
    "TEXT_PREVIEW",
    "WIDGETS_PADDING",
    "WIDGET_GAP",
    "WIDGET_HEIGHT",
]

"""The host nodes the build scripts name."""

IMAGE = "LoadImage"
NOTE = "MarkdownNote"
PREVIEW = "PreviewAny"
TEXT = "PrimitiveString"
TEXT_BLOCK = "PrimitiveStringMultiline"
FOLDER_IMAGES = "LoadImageDataSetFromFolder"
SAVE_CAPTIONS = "SaveImageTextDataSetToFolder"
SAVE_IMAGE = "SaveImage"
SAVE_TEXT = "SaveText"
SAVE_SVG = "SaveSVGNode"
AUDIO = "LoadAudio"
SAVE_AUDIO = "SaveAudioAdvanced"
PREVIEW_AUDIO = "PreviewAudio"
SAVE_VIDEO = "SaveVideo"
FORMAT = "StringFormat"
COMPARE = "StringCompare"
FIELD = "JsonExtractString"
SWITCH = "ComfySwitchNode"
# ComfyUI nodes the workflows place beside this extension's own.
HOST_NODES = (
    IMAGE,
    PREVIEW,
    TEXT,
    TEXT_BLOCK,
    FOLDER_IMAGES,
    SAVE_CAPTIONS,
    SAVE_IMAGE,
    SAVE_TEXT,
    SAVE_SVG,
    AUDIO,
    SAVE_AUDIO,
    PREVIEW_AUDIO,
    SAVE_VIDEO,
    FORMAT,
    COMPARE,
    FIELD,
    SWITCH,
)

__all__ = [
    "AUDIO",
    "COMPARE",
    "FIELD",
    "FOLDER_IMAGES",
    "FORMAT",
    "HOST_NODES",
    "IMAGE",
    "NOTE",
    "PREVIEW",
    "PREVIEW_AUDIO",
    "SAVE_AUDIO",
    "SAVE_CAPTIONS",
    "SAVE_IMAGE",
    "SAVE_SVG",
    "SAVE_TEXT",
    "SAVE_VIDEO",
    "SWITCH",
    "TEXT",
    "TEXT_BLOCK",
]

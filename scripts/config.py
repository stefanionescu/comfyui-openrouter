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
BATCH = "BatchImagesNode"
FROM_BATCH = "ImageFromBatch"
MASK_IMAGE = "MaskToImage"
PREVIEW_IMAGE = "PreviewImage"
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
    BATCH,
    FROM_BATCH,
    MASK_IMAGE,
    PREVIEW_IMAGE,
)

__all__ = [
    "AUDIO",
    "BATCH",
    "COMPARE",
    "FIELD",
    "FOLDER_IMAGES",
    "FORMAT",
    "FROM_BATCH",
    "HOST_NODES",
    "IMAGE",
    "MASK_IMAGE",
    "NOTE",
    "PREVIEW",
    "PREVIEW_AUDIO",
    "PREVIEW_IMAGE",
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

"""The ComfyUI nodes the example workflows place beside this extension's own."""

from enum import StrEnum


class HostNode(StrEnum):
    """One ComfyUI node, by the name ComfyUI registers it under."""

    IMAGE = "LoadImage"
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
    JOIN_ALPHA = "JoinImageWithAlpha"


__all__ = ["HostNode"]

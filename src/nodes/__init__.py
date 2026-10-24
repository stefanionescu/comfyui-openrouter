"""Register the extension's nodes in menu order."""

from comfy_api.latest import io

from .image import ImageGenerate
from .model import ModelInfo
from .options import RequestOptions
from .chat.ask import ChatAsk
from .audio.speak import AudioSpeak
from .search.rank import SearchRank
from .decision.ask import DecisionAsk
from .search.embed import SearchEmbed
from .chat.document import ChatAttachDocument
from .video.download import VideoDownload
from .video.generate import VideoGenerate
from .decision.answer import DecisionReadAnswer
from .audio.transcribe import AudioTranscribe
from .decision.question import DecisionAddQuestion

NODE_TYPES: tuple[type[io.ComfyNode], ...] = (
    ChatAsk,
    ChatAttachDocument,
    ImageGenerate,
    VideoGenerate,
    VideoDownload,
    AudioSpeak,
    AudioTranscribe,
    SearchEmbed,
    SearchRank,
    DecisionAsk,
    DecisionAddQuestion,
    DecisionReadAnswer,
    RequestOptions,
    ModelInfo,
)

__all__ = ['NODE_TYPES']

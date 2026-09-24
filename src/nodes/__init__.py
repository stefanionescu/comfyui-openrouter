"""Register the extension's nodes in menu order."""

from .chat.ask import ChatAsk
from comfy_api.latest import io
from .image import ImageGenerate
from .audio.speak import AudioSpeak
from .options import RequestOptions
from .search.rank import SearchRank
from .decision.ask import DecisionAsk
from .search.embed import SearchEmbed
from .video.download import VideoDownload
from .video.generate import VideoGenerate
from .audio.transcribe import AudioTranscribe
from .chat.document import ChatAttachDocument
from .decision.answer import DecisionReadAnswer
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
)

__all__ = ["NODE_TYPES"]

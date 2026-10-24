"""The node IDs of this extension that the shipped workflows place, and the model IDs several workflows choose."""

from src.config.namespace import NODE_PREFIX

CHAT_ASK = f'{NODE_PREFIX}ChatAsk'
CHAT_ATTACH_DOCUMENT = f'{NODE_PREFIX}ChatAttachDocument'
IMAGE_GENERATE = f'{NODE_PREFIX}ImageGenerate'
VIDEO_GENERATE = f'{NODE_PREFIX}VideoGenerate'
VIDEO_DOWNLOAD = f'{NODE_PREFIX}VideoDownload'
AUDIO_SPEAK = f'{NODE_PREFIX}AudioSpeak'
AUDIO_TRANSCRIBE = f'{NODE_PREFIX}AudioTranscribe'
SEARCH_EMBED = f'{NODE_PREFIX}SearchEmbed'
SEARCH_RANK = f'{NODE_PREFIX}SearchRank'
DECISION_ASK = f'{NODE_PREFIX}DecisionAsk'
DECISION_ADD_QUESTION = f'{NODE_PREFIX}DecisionAddQuestion'
DECISION_READ_ANSWER = f'{NODE_PREFIX}DecisionReadAnswer'
REQUEST_OPTIONS = f'{NODE_PREFIX}RequestOptions'
MODEL_INFO = f'{NODE_PREFIX}ModelInfo'

# The models the workflows choose instead of the node default: a writer, a reader of images, and an image model.
WRITER = 'openai/gpt-6-sol'
READER = 'openai/gpt-6-luna'
GPT_IMAGE = 'openai/gpt-image-2.5-flare'

__all__ = [
    'AUDIO_SPEAK',
    'AUDIO_TRANSCRIBE',
    'CHAT_ASK',
    'CHAT_ATTACH_DOCUMENT',
    'DECISION_ADD_QUESTION',
    'DECISION_ASK',
    'DECISION_READ_ANSWER',
    'GPT_IMAGE',
    'IMAGE_GENERATE',
    'MODEL_INFO',
    'READER',
    'REQUEST_OPTIONS',
    'SEARCH_EMBED',
    'SEARCH_RANK',
    'VIDEO_DOWNLOAD',
    'VIDEO_GENERATE',
    'WRITER',
]

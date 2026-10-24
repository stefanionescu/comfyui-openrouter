"""Chat: Ask and Chat: Attach Document choices."""

from .inputs import MODEL_DEFAULT

# The sampling fields OpenRouter takes, in node order.
SAMPLING = (
    'temperature',
    'top_p',
    'top_k',
    'min_p',
    'top_a',
    'frequency_penalty',
    'presence_penalty',
    'repetition_penalty',
)

# Each sampling field that takes decimals, as the value custom starts at, which is OpenRouter's default, the
# documented minimum and maximum, and the step.
SAMPLING_DECIMALS = {
    'temperature': (1.0, 0.0, 2.0, 0.05),
    'top_p': (1.0, 0.0, 1.0, 0.01),
    'min_p': (0.0, 0.0, 1.0, 0.01),
    'top_a': (0.0, 0.0, 1.0, 0.01),
    'frequency_penalty': (0.0, -2.0, 2.0, 0.05),
    'presence_penalty': (0.0, -2.0, 2.0, 0.05),
    'repetition_penalty': (1.0, 0.0, 2.0, 0.05),
}

# Each sampling field that takes whole numbers, as the value custom starts at, which is OpenRouter's default, and the
# documented minimum; OpenRouter documents no maximum.
SAMPLING_WHOLE_NUMBERS = {
    'top_k': (0, 0),
}

# What each sampling field does, for its tooltip.
SAMPLING_TOOLTIPS = {
    'temperature': 'How much the answer varies.',
    'top_p': 'The share of likely words the model picks from; lower keeps the answer more focused.',
    'top_k': 'How many of the most likely words the model picks from; 0 means all of them.',
    'min_p': 'The least chance a word needs, as a share of the chance of the most likely word.',
    'top_a': 'Drops unlikely words more, the more likely the most likely word is.',
    'frequency_penalty': 'Above 0, the model repeats a word less the more often it has appeared.',
    'presence_penalty': 'Above 0, the model repeats less any word that has appeared.',
    'repetition_penalty': 'Above 1, the model repeats words from the prompt and the answer less.',
}

# How much a reasoning model thinks.
EFFORTS = (MODEL_DEFAULT, 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max')

# What each outputs choice asks the model to make besides text.
OUTPUTS = {'text': (), 'image and text': ('image',), 'audio and text': ('audio',)}

# The shape of the images a chat model makes.
IMAGE_ASPECT_RATIOS = (MODEL_DEFAULT, '1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9')

# How OpenRouter reads PDFs.
PDF_ENGINES = (MODEL_DEFAULT, 'native', 'cloudflare-ai', 'mistral-ocr')

# The voice a spoken reply starts with, and the format voice chat models stream; asking for WAV fails with a
# provider error.
VOICE = {
    'DEFAULT': 'alloy',
    'FORMAT': 'pcm16',
}

# Voice chat models stream 16-bit PCM at this rate, in mono.
VOICE_AUDIO = {
    'SAMPLE_RATE': 24_000,
    'CHANNELS': 1,
}

# A PDF goes to OpenRouter's PDF engine; any other document goes as text.
PDF_MEDIA_TYPE = 'application/pdf'

# The document files the input folder may hold, with the media type the extension sends for each.
DOCUMENT_TYPES = {
    '.pdf': PDF_MEDIA_TYPE,
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.csv': 'text/csv',
    '.json': 'application/json',
}

__all__ = [
    'DOCUMENT_TYPES',
    'EFFORTS',
    'IMAGE_ASPECT_RATIOS',
    'OUTPUTS',
    'PDF_ENGINES',
    'PDF_MEDIA_TYPE',
    'SAMPLING',
    'SAMPLING_DECIMALS',
    'SAMPLING_TOOLTIPS',
    'SAMPLING_WHOLE_NUMBERS',
    'VOICE',
    'VOICE_AUDIO',
]

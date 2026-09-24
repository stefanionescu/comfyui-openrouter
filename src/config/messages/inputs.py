"""Messages for node inputs the extension refuses before sending anything."""

ANSWER_SCHEMA_INVALID = "The answer schema must be a JSON object that describes the answer."
CHOICE_OPTIONS = "List {minimum} to {maximum} options, one per line, as key: description."
CHOICE_OPTION_REPEATED = "Each option needs its own key; {key} is listed twice."
CONVERSATION_LIMIT = "The conversation has more than {maximum} turns. Start a new conversation."
DOCUMENT_KIND = "Choose a PDF, text, Markdown, CSV, or JSON document."
DOCUMENT_LIMIT = "Attach at most {maximum} documents to one request."
DOCUMENT_MISSING = "Put a PDF or text file in ComfyUI's input folder, press R, and choose it."
DOCUMENT_OUTSIDE = "Choose a document inside ComfyUI's input folder."
DOCUMENT_SIZE = "The document is larger than the maximum upload size of {maximum} MiB in OpenRouter settings."
DOCUMENT_UNREADABLE = "The document could not be read as UTF-8 text. Save it as UTF-8 or as a PDF."
LANGUAGE_CODE = "Enter a two-letter language code such as en, or leave the language empty."
OPTIONS_JSON = "Write {field} as a JSON object, or leave it empty."
OPTIONS_SIZE = "Keep {field} under 64 KB."
OPTION_RESERVED_FIELD = "The node sets {field} itself. Remove it from the extra fields in Request Options."
OPTION_UNSUPPORTED = (
    "OpenRouter's {endpoint} requests do not accept {field}. Remove it from Request Options for this node."
)
PCM_RATE_MISSING = (
    "OpenRouter sent PCM audio without its sample rate and channels. Choose mp3 as the audio format and run again."
)
PROMPT_EMPTY = "Write a prompt."
PROMPT_LENGTH = "Write a prompt of at most {maximum} characters."
PROVIDER_SLUG = "Write providers as OpenRouter slugs such as google-vertex, separated by commas, at most {maximum}."
QUERY_EMPTY = "Write the query to rank against."
QUESTION_INSTRUCTIONS = "Write what the question asks."
QUESTION_LIMIT = "Ask at most {maximum} questions in one decision."
QUESTION_NAME = "Name the question with lowercase letters, digits, and underscores, starting with a letter."
QUESTION_REPEATED = "Each question needs its own name; {name} is used twice."
QUESTION_UNKNOWN = "There is no question named {name}. The questions are: {names}."
SCORE_LEVELS = "List {minimum} to {maximum} levels, one per line, from lowest to highest."
SEARCH_ITEMS_EMPTY = "Enter at least one line of text or connect an image."
SEARCH_ITEMS_LIMIT = "Send at most {maximum} items at once."
SINGLE_VALUE = "Connect one value to {name}, not a list."
SITUATION_EMPTY = "Describe the situation to decide on."
SITUATION_LENGTH = "Describe the situation in at most {maximum} characters."
SPEECH_TEXT_EMPTY = "Write the text to speak."
SPEECH_TEXT_LENGTH = "Write at most {maximum} characters to speak. Split longer text across several nodes."
TRANSPARENT_FORMAT = "A transparent background needs the PNG or WebP file format."
VOICE_SAMPLE_SIZE = "Use a voice sample of at most 15 MiB."
YES_NO_CRITERIA = "Describe both when the answer is yes and when it is no, or leave both empty."

__all__ = [
    "ANSWER_SCHEMA_INVALID",
    "CHOICE_OPTIONS",
    "CHOICE_OPTION_REPEATED",
    "CONVERSATION_LIMIT",
    "DOCUMENT_KIND",
    "DOCUMENT_LIMIT",
    "DOCUMENT_MISSING",
    "DOCUMENT_OUTSIDE",
    "DOCUMENT_SIZE",
    "DOCUMENT_UNREADABLE",
    "LANGUAGE_CODE",
    "OPTIONS_JSON",
    "OPTIONS_SIZE",
    "OPTION_RESERVED_FIELD",
    "OPTION_UNSUPPORTED",
    "PCM_RATE_MISSING",
    "PROMPT_EMPTY",
    "PROMPT_LENGTH",
    "PROVIDER_SLUG",
    "QUERY_EMPTY",
    "QUESTION_INSTRUCTIONS",
    "QUESTION_LIMIT",
    "QUESTION_NAME",
    "QUESTION_REPEATED",
    "QUESTION_UNKNOWN",
    "SCORE_LEVELS",
    "SEARCH_ITEMS_EMPTY",
    "SEARCH_ITEMS_LIMIT",
    "SINGLE_VALUE",
    "SITUATION_EMPTY",
    "SITUATION_LENGTH",
    "SPEECH_TEXT_EMPTY",
    "SPEECH_TEXT_LENGTH",
    "TRANSPARENT_FORMAT",
    "VOICE_SAMPLE_SIZE",
    "YES_NO_CRITERIA",
]

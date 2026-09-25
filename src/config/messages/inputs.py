"""Messages for node inputs the extension refuses before sending anything."""

ANSWER_SCHEMA_INVALID = "The answer schema must be a JSON object that describes the answer."
CHOICE_OPTIONS = "List at least one option, one per line, as key: description."
CHOICE_OPTION_REPEATED = "Each option needs its own key; {key} is listed twice."
DOCUMENT_KIND = "Choose a PDF, text, Markdown, CSV, or JSON document."
DOCUMENT_MISSING = "Put a PDF or text file in ComfyUI's input folder, press R, and choose it."
DOCUMENT_OUTSIDE = "Choose a document inside ComfyUI's input folder."
DOCUMENT_SIZE = "The document is larger than the maximum upload size of {maximum} MiB in OpenRouter settings."
DOCUMENT_UNREADABLE = "The document could not be read as UTF-8 text. Save it as UTF-8 or as a PDF."
LANGUAGE_CODE = "Enter a two-letter language code such as en, or leave the language empty."
OPTIONS_JSON = "Write {field} as a JSON object, or leave it empty."
OPTION_RESERVED_FIELD = "The node sets {field} itself. Remove it from the extra fields in Request Options."
OPTION_UNSUPPORTED = (
    "OpenRouter's {endpoint} requests do not accept {field}. Remove it from Request Options for this node."
)
PCM_RATE_MISSING = (
    "OpenRouter sent PCM audio without its sample rate and channels. Choose mp3 as the audio format and run again."
)
PROMPT_EMPTY = "Write a prompt."
PROVIDER_SLUG = "Write providers as OpenRouter slugs such as google-vertex, separated by commas."
QUERY_EMPTY = "Write the query to rank against."
QUESTION_INSTRUCTIONS = "Write what the question asks."
QUESTION_NAME = "Name the question with lowercase letters, digits, and underscores, starting with a letter."
QUESTION_REPEATED = "Each question needs its own name; {name} is used twice."
QUESTION_UNKNOWN = "There is no question named {name}. The questions are: {names}."
SCORE_LEVELS = "List at least one level, one per line, from lowest to highest."
SEARCH_ITEMS_EMPTY = "Enter at least one line of text or connect an image."
SINGLE_VALUE = "Connect one value to {name}, not a list."
SITUATION_EMPTY = "Describe the situation to decide on."
SPEECH_TEXT_EMPTY = "Write the text to speak."
TRANSPARENT_FORMAT = "A transparent background needs the PNG or WebP file format."
YES_NO_CRITERIA = "Describe both when the answer is yes and when it is no, or leave both empty."

__all__ = [
    "ANSWER_SCHEMA_INVALID",
    "CHOICE_OPTIONS",
    "CHOICE_OPTION_REPEATED",
    "DOCUMENT_KIND",
    "DOCUMENT_MISSING",
    "DOCUMENT_OUTSIDE",
    "DOCUMENT_SIZE",
    "DOCUMENT_UNREADABLE",
    "LANGUAGE_CODE",
    "OPTIONS_JSON",
    "OPTION_RESERVED_FIELD",
    "OPTION_UNSUPPORTED",
    "PCM_RATE_MISSING",
    "PROMPT_EMPTY",
    "PROVIDER_SLUG",
    "QUERY_EMPTY",
    "QUESTION_INSTRUCTIONS",
    "QUESTION_NAME",
    "QUESTION_REPEATED",
    "QUESTION_UNKNOWN",
    "SCORE_LEVELS",
    "SEARCH_ITEMS_EMPTY",
    "SINGLE_VALUE",
    "SITUATION_EMPTY",
    "SPEECH_TEXT_EMPTY",
    "TRANSPARENT_FORMAT",
    "YES_NO_CRITERIA",
]

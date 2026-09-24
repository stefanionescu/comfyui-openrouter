# Audio: Transcribe

Turns speech into text with any transcription model on OpenRouter, with timed
segments, timed words, and subtitles if you ask for them. Each run is one paid
request, priced per second of audio; prices are in **OpenRouter models**.

## Inputs

| Input         | What it takes                                                                                                     |
| ------------- | ----------------------------------------------------------------------------------------------------------------- |
| `audio`       | One clip. It is sent as WAV.                                                                                      |
| `model`       | Any transcription model; the default is `openai/whisper-large-v3-turbo`. Choose **other model ID** to type an ID. |
| `language`    | The spoken language as a two-letter code, such as `en`. Leave it empty to detect it.                              |
| `timestamps`  | `none`, `segments`, or `words and segments`, for models that return timestamps.                                   |
| `temperature` | 0 to 1; 0 leaves it to the model.                                                                                 |
| `variation`   | **run number**: change it to send the same request again.                                                         |
| `options`     | Settings from **Request Options**.                                                                                |

## Outputs

| Output      | What it carries                                                                            |
| ----------- | ------------------------------------------------------------------------------------------ |
| `text`      | The transcript.                                                                            |
| `segments`  | A JSON list of `start`, `end`, `text`, and `speaker` per segment; `[]` without timestamps. |
| `subtitles` | SRT subtitles; empty without timestamps.                                                   |
| `words`     | A JSON list of `start`, `end`, and `text` per word; `[]` unless you ask for words.         |

## Use

1. Connect the audio and choose the model.
2. Connect **text** to **Save Text** or **Preview as Text**.
3. Select **Run**.

Examples: **audio-01-triage-a-voicemail** and **audio-02-dub-a-clip**.
Providers stop after about 60 seconds of processing, so split long recordings.

[OpenRouter speech-to-text documentation](https://openrouter.ai/docs/guides/overview/multimodal/stt)

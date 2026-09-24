# Audio: Transcribe

Turn speech into text, timed segments and words, and subtitles with any OpenRouter transcription model. Connect **text** to **Save Text** or **Preview as Text**. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input         | What it takes                                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `audio`       | One clip, from **Load Audio** or another node. It is sent as WAV.                                                           |
| `model`       | Every OpenRouter transcription model; by default `openai/whisper-large-v3-turbo`. Choose **other model ID** to type any ID. |
| `language`    | The spoken language as two letters, such as `en`; leave empty to let the model detect it.                                   |
| `timestamps`  | `none`, `segments`, or `words and segments`, which also times each word. Not every model returns timestamps.                |
| `temperature` | From 0 to 1; 0 leaves it to the model.                                                                                      |
| `variation`   | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed.                 |
| `options`     | From **Request Options**, to pass provider options.                                                                         |

## Outputs

| Output      | What it carries                                                                                     |
| ----------- | --------------------------------------------------------------------------------------------------- |
| `text`      | The whole transcript.                                                                               |
| `segments`  | A JSON list of `start`, `end`, `text`, and `speaker` per segment; `[]` without timestamps.          |
| `subtitles` | SRT subtitles built from the segments; empty without timestamps.                                    |
| `words`     | A JSON list of `start`, `end`, and `text` per word; `[]` unless timestamps is `words and segments`. |

## Run

1. To start from a finished workflow, open **audio-01-triage-a-voicemail** or **audio-02-dub-a-clip** from **Browse Templates → comfyui-openrouter**.
1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Connect the audio and choose the model.
1. Select **Run**.

Providers stop after about 60 seconds of processing, so split long recordings before sending them. Transcription is billed by the second, rounded up.

Review a transcript before you rely on it; names and numbers are the most common errors.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter speech-to-text documentation](https://openrouter.ai/docs/guides/overview/multimodal/stt)

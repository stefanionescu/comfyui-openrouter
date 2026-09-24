# Audio: Speak

Turns text into speech with any speech model on OpenRouter. Some models can
copy a voice from a sample. Each run is one paid request, priced per character;
prices are in **OpenRouter models**.

## Inputs

| Input                | What it takes                                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `text`               | What to say, up to 100,000 characters.                                                                           |
| `model`              | Any speech model; the default is `google/gemini-3.1-flash-tts-preview`. Choose **other model ID** to type an ID. |
| `model.voice`        | The voice, from the model's voice list; otherwise the model's default voice.                                     |
| `model.audio_format` | `pcm` or `mp3`. If the model refuses one, choose the other.                                                      |
| `speed`              | Speaking speed. Some providers ignore it.                                                                        |
| `voice_sample`       | A short clip of the voice to copy, up to 15 MiB, for models that clone voices.                                   |
| `sample_transcript`  | The words spoken in the sample.                                                                                  |
| `variation`          | **run number**: change it to send the same request again.                                                        |
| `options`            | Settings from **Request Options**.                                                                               |

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `audio` | The speech.     |

## Use

1. Write the text, and choose the model and voice.
2. Connect **audio** to **Save Audio (Advanced)** or **Preview Audio**.
3. Select **Run**.

Examples: **audio-01-triage-a-voicemail** and **audio-02-dub-a-clip**. Gemini
voices send only PCM, and MiniMax voices only MP3, which is their default here.
Clone a voice only with the owner's permission.

[OpenRouter text-to-speech documentation](https://openrouter.ai/docs/guides/overview/multimodal/tts)

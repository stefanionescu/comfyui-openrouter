# Audio: Speak

Turns text into speech with any speech model on OpenRouter. Some models can copy
a voice from a sample.

## Inputs

| Input               | What it takes                                                                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `model`             | Any speech model ID from openrouter.ai/models; the default is `google/gemini-3.1-flash-tts-preview`.                                      |
| `voice`             | The voice ID, such as `Kore` for Gemini or `alloy` for OpenAI. The default, `Kore`, suits the default model; leave it empty to send none. |
| `audio_format`      | `pcm` or `mp3`. If the model refuses one, choose the other; MiniMax models send only `mp3`.                                               |
| `speed`             | Speaking speed. Some providers ignore it.                                                                                                 |
| `sample_transcript` | The words spoken in the sample.                                                                                                           |
| `run_number`        | Change it to send the same request again.                                                                                                 |
| `text`              | What to say, up to 100,000 characters.                                                                                                    |
| `voice_sample`      | A short clip of the voice to copy, up to 15 MiB, for models that clone voices.                                                            |
| `options`           | Settings from **Request Options**.                                                                                                        |

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `audio` | The speech.     |

## Use

1. Write the text, and type the model ID and voice.
2. Connect **audio** to **Save Audio (Advanced)** or **Preview Audio**.
3. Select **Run**.

Examples: **audio-01-triage-a-voicemail** and **audio-02-dub-a-clip**. Gemini
voices send only PCM, and MiniMax voices only MP3, which is their default here.
Clone a voice only with the owner's permission.

[OpenRouter text-to-speech documentation](https://openrouter.ai/docs/guides/overview/multimodal/tts)

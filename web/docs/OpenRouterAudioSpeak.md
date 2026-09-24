# Audio: Speak

Turn text into speech with any OpenRouter speech model. Connect **audio** to **Save Audio (Advanced)** or **Preview Audio**. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input                | What it takes                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `text`               | What to say, up to 100,000 characters.                                                                                     |
| `model`              | Every OpenRouter speech model; by default `google/gemini-3.1-flash-tts-preview`. Choose **other model ID** to type any ID. |
| `model.voice`        | The voice, from the voices the model lists. A model without a list uses its provider's default voice.                      |
| `model.audio_format` | The format OpenRouter sends: `pcm` or `mp3`. Most models send both; if the model refuses one, choose the other.            |
| `speed`              | Speaking speed; some providers ignore it.                                                                                  |
| `voice_sample`       | A short clip of the voice to copy. Only models that clone voices use it; at most 15 MiB.                                   |
| `sample_transcript`  | What the sample says.                                                                                                      |
| `variation`          | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed.                |
| `options`            | From **Request Options**, to pass provider options.                                                                        |

## Outputs

| Output  | What it carries |
| ------- | --------------- |
| `audio` | The speech.     |

## Run

1. To start from a finished workflow, open **audio-01-triage-a-voicemail** or **audio-02-dub-a-clip** from **Browse Templates → comfyui-openrouter**.
1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write the text and choose the model and voice.
1. Select **Run**.

Speech is priced per character. Only some models clone voices; the others ignore **voice sample**. Gemini voices send only PCM, and MiniMax voices only MP3, which is their default here.

Copy only a voice you own or have permission to use.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter text-to-speech documentation](https://openrouter.ai/docs/guides/overview/multimodal/tts)

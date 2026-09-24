# Chat: Ask

Asks a chat model a question, with images, video, audio, or documents if the
model reads them. Returns text, and images or speech from models that make
them. Each run is one paid request; prices are in **OpenRouter models**.

## Inputs

| Input                     | What it takes                                                                                                                                                                                                        |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`                  | The question or instruction.                                                                                                                                                                                         |
| `model`                   | Any chat model; the default is `google/gemini-3.5-flash`. Choose **other model ID** to type an ID, such as one ending in `:nitro`.                                                                                   |
| `model.reasoning`         | How much a reasoning model thinks before answering.                                                                                                                                                                  |
| `model.max_output_tokens` | The longest answer in tokens; 0 leaves it to the model.                                                                                                                                                              |
| `model.temperature`       | 0 to 2. Higher values vary the answer more.                                                                                                                                                                          |
| `model.answer_schema`     | A JSON schema the answer must follow. Leave it empty for free text.                                                                                                                                                  |
| `model.images`            | Images, one per socket, up to 16. Every image in a batch is sent.                                                                                                                                                    |
| `model.videos`            | Videos, one per socket, up to 4. Each is sent as MP4.                                                                                                                                                                |
| `model.audio`             | Audio clips, one per socket, up to 4. Each is sent as WAV.                                                                                                                                                           |
| `model.outputs`           | For models that draw or speak: **text**, **image and text**, or **audio and text**.                                                                                                                                  |
| `model.aspect_ratio`      | The shape of the images a model draws.                                                                                                                                                                               |
| `model.voice`             | The voice of a spoken answer, such as `alloy`. Music models need it empty.                                                                                                                                           |
| `system`                  | The system prompt: instructions for the whole answer.                                                                                                                                                                |
| `conversation`            | Earlier turns, from another **Chat: Ask**.                                                                                                                                                                           |
| `documents`               | Files from **Chat: Attach Document**.                                                                                                                                                                                |
| `pdf_engine`              | How OpenRouter reads PDFs: `native` (billed as input tokens), `cloudflare-ai` (free), or `mistral-ocr` ($2 per 1,000 pages). **model default** uses the model's own file reading, or `mistral-ocr` when it has none. |
| `seed`                    | Varies the output, for models that take a seed.                                                                                                                                                                      |
| `variation`               | **run number**: change it to send the same request again.                                                                                                                                                            |
| `options`                 | Settings from **Request Options**.                                                                                                                                                                                   |

## Outputs

| Output         | What it carries                                                                      |
| -------------- | ------------------------------------------------------------------------------------ |
| `text`         | The answer, or the words of a spoken answer. Some drawing models return only images. |
| `reasoning`    | The model's reasoning, if it shares it.                                              |
| `images`       | The images the model made. Connected nodes are skipped when it is empty.             |
| `audio`        | The spoken or musical answer. Connected nodes are skipped when it is empty.          |
| `conversation` | The earlier turns plus this question and answer, for the next **Chat: Ask**.         |

## Use

1. Write the prompt and choose the model.
2. Connect any media the model reads.
3. Connect **text** to **Preview as Text**, and select **Run**.

The settings under **model** change with the model: each model shows only what
it accepts. Examples: **chat-01-write-a-product-listing** and
**chat-02-caption-a-training-set** in **Browse Templates → comfyui-openrouter**.

A list of images, such as from **Load Image (from Folder)**, runs the node once
per image, and each run is billed. To send several images in one request,
connect each to its own socket.

An answer that stops mid-sentence hit the token limit; raise
**max_output_tokens**. Cancelling stops the wait; the tokens produced so far are
billed. For factual answers, attach the documents the model should answer from.

[OpenRouter multimodal documentation](https://openrouter.ai/docs/guides/overview/multimodal/overview)

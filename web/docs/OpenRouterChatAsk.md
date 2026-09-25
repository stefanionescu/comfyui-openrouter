# Chat: Ask

Asks a chat model a question, with images, video, audio, or documents if the
model reads them. Returns text, and images or speech from models that make them.

## Inputs

| Input              | What it takes                                                                                                                                                   |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`            | Any chat model ID from openrouter.ai/models; the default is `google/gemini-3.5-flash`. A suffix such as `:nitro` picks a variant.                               |
| `images`           | Images: one, a batch, or a list. Each goes in the request at its own size.                                                                                      |
| `videos`           | Videos: one or a list. Each is sent as MP4.                                                                                                                     |
| `audio`            | Audio clips: one, a batch, or a list. Each is sent as WAV.                                                                                                      |
| `reasoning_effort` | How much a reasoning model thinks before answering. Sent only to models that reason.                                                                            |
| `max_tokens`       | The longest answer in tokens; 0 leaves it to the model.                                                                                                         |
| `temperature`      | **model default** sends none. **set** sends a value from 0 to 2; higher values vary the answer more. Sent only to models that take a temperature.               |
| `outputs`          | **text**, **image and text**, or **audio and text**. Images and audio need a model that makes them.                                                             |
| `aspect_ratio`     | The shape of the images a model draws.                                                                                                                          |
| `voice`            | The voice of a spoken answer, such as `alloy`. Music models need it empty.                                                                                      |
| `pdf_engine`       | How OpenRouter reads PDFs: `native`, `cloudflare-ai`, or `mistral-ocr`. **model default** uses the model's own file reading, or `mistral-ocr` when it has none. |
| `seed`             | Varies the output, for models that take a seed.                                                                                                                 |
| `run_number`       | Change it to send the same request again.                                                                                                                       |
| `answer_schema`    | A JSON schema the answer must follow; only providers that follow it answer. Leave it empty for free text.                                                       |
| `prompt`           | The question or instruction.                                                                                                                                    |
| `conversation`     | Earlier turns, from another **Chat: Ask**.                                                                                                                      |
| `documents`        | Files from **Chat: Attach Document**.                                                                                                                           |
| `options`          | Settings from **Request Options**.                                                                                                                              |
| `system_prompt`    | The system prompt: instructions for the whole answer.                                                                                                           |

## Outputs

| Output         | What it carries                                                                      |
| -------------- | ------------------------------------------------------------------------------------ |
| `text`         | The answer, or the words of a spoken answer. Some drawing models return only images. |
| `reasoning`    | The model's reasoning, if it shares it.                                              |
| `images`       | The images the model made. Connected nodes are skipped when it is empty.             |
| `audio`        | The spoken or musical answer. Connected nodes are skipped when it is empty.          |
| `conversation` | The earlier turns plus this question and answer, for the next **Chat: Ask**.         |

## Use

1. Write the prompt and type the model ID.
2. Connect any media the model reads.
3. Connect **text** to **Preview as Text**, and select **Run**.

Examples: **chat-01-write-a-product-listing** and
**chat-02-caption-a-training-set**.

Everything connected to **images**, **videos**, and **audio** goes in one
request: one item, a batch, a list such as **Load Image (from Folder)** makes,
or several **Load Image** nodes joined by **Create List**. Images keep their own
sizes.

Before anything is paid, the node refuses media the model does not read,
outputs it does not make, an answer schema it cannot follow, and max tokens
above its longest answer.

An answer that stops mid-sentence hit the token limit; raise **max tokens**.

[OpenRouter multimodal documentation](https://openrouter.ai/docs/guides/overview/multimodal/overview)

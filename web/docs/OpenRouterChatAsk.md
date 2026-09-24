# Chat: Ask

Ask any OpenRouter chat model a question, with images, video, audio, and documents when the model accepts them, and get back text, reasoning, generated images, or spoken audio. Connect **text** to **Preview as Text**, and **conversation** to another **Chat: Ask** to continue. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input                     | What it takes                                                                                                                                               |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prompt`                  | The question or instruction.                                                                                                                                |
| `model`                   | Every OpenRouter model that answers with text; by default `google/gemini-3.5-flash`. Choose **other model ID** to type any ID, such as a `:online` variant. |
| `model.reasoning`         | How much a reasoning model thinks before answering, from the efforts the model lists.                                                                       |
| `model.max_output_tokens` | The longest answer in tokens, up to the model's limit; 0 leaves it to the model.                                                                            |
| `model.temperature`       | Higher values vary the answer more, from 0 to 2.                                                                                                            |
| `model.answer_schema`     | A JSON schema the answer must follow, for models that support structured output; leave empty for free text.                                                 |
| `model.images`            | Images for a model that reads images, one per socket, up to 16. Every image of a batch is sent.                                                             |
| `model.videos`            | Videos for a model that reads video, one per socket, up to 4. Each is sent as MP4.                                                                          |
| `model.audio`             | Audio clips for a model that reads audio, one per socket, up to 4. Each is sent as WAV.                                                                     |
| `model.outputs`           | For a model that draws or speaks: **text**, or **image and text**, or **audio and text**.                                                                   |
| `model.aspect_ratio`      | The shape of generated images, for a chat model that draws.                                                                                                 |
| `model.voice`             | The voice of spoken replies, such as `alloy`. Voice models need a voice; music models need it blank.                                                        |
| `system`                  | Instructions the model follows for the whole answer.                                                                                                        |
| `conversation`            | The earlier turns, from another **Chat: Ask**.                                                                                                              |
| `documents`               | Files from **Chat: Attach Document**. OpenRouter reads PDFs for models without file input.                                                                  |
| `pdf_engine`              | How OpenRouter reads PDFs: the model's default, `native`, `cloudflare-ai`, or `mistral-ocr`.                                                                |
| `seed`                    | Number used by the model to vary its output, sent when the model accepts a seed.                                                                            |
| `variation`               | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed.                                                 |
| `options`                 | From **Request Options**, to choose providers or pass extra fields.                                                                                         |

## Outputs

| Output         | What it carries                                                                                               |
| -------------- | ------------------------------------------------------------------------------------------------------------- |
| `text`         | The answer; for a spoken answer, the words spoken. Some models that draw return only the image, with no text. |
| `reasoning`    | The model's reasoning when it shares it; otherwise empty.                                                     |
| `images`       | A list of generated images, each at its own size; the nodes connected to it do not run when there are none.   |
| `audio`        | The spoken or musical answer; the nodes connected to it do not run when there is none.                        |
| `conversation` | The earlier turns with this question and answer added.                                                        |

## Run

1. To start from a finished workflow, open **chat-01-write-a-product-listing** or **chat-02-caption-a-training-set** from **Browse Templates → comfyui-openrouter**.
1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write the prompt, choose the model, and connect the media it reads.
1. Select **Run**.

The controls under **model** change with the model: a model only shows the settings, sockets, and outputs it accepts. When a list, such as the images of **Load Image (from Folder)**, reaches an image socket, ComfyUI runs the node once per image, and each run is a paid request. To send several images in one request, connect each to its own socket; each keeps its own size.

An answer that stops mid-sentence reached the output token limit; raise **max output tokens**. ComfyUI's cancel stops waiting, but tokens the model produced before a cancel are billed. **Chat: Ask** returns images without masks; for masks, use **Image: Generate**. ComfyUI reuses a cached answer when nothing changed; the seed changes after each run unless its control is **fixed**.

Models can state wrong facts with confidence. Check an answer before you rely on it, and give the model the documents it should answer from.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter multimodal documentation](https://openrouter.ai/docs/guides/overview/multimodal/overview)

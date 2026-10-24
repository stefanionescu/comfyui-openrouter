# Chat: Ask

Asks a chat model a question, with images, video, audio, or documents if the
model reads them. Returns text, and images or speech from models that make them.

## Inputs

| Input                | What it takes                                                                                                                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `model`              | Any chat model ID from openrouter.ai/models; the default is `google/gemini-3.5-flash`. A suffix such as `:nitro` picks a variant.                                                             |
| `images`             | Images: one, a batch, or a list. Each goes in the request at its own size.                                                                                                                    |
| `videos`             | Videos: one or a list. Each is sent as MP4.                                                                                                                                                   |
| `audio`              | Audio clips: one, a batch, or a list. Each is sent as WAV.                                                                                                                                    |
| `reasoning_effort`   | How much a reasoning model thinks before answering. Sent only to models that reason. A level the model does not list steps down to the highest it lists below it, or up to its lowest.        |
| `max_tokens`         | The longest answer in tokens; 0 leaves it to the model.                                                                                                                                       |
| `temperature`        | `default` sends none. `custom` sends a value from 0 to 2; higher values vary the answer more.                                                                                                 |
| `top_p`              | `default` sends none. `custom` sends a share from 0 to 1 of the likely words the model picks from.                                                                                            |
| `top_k`              | `default` sends none. `custom` sends how many of the most likely words the model picks from; 0 means all.                                                                                     |
| `min_p`              | `default` sends none. `custom` sends the least chance a word needs, from 0 to 1, as a share of the chance of the most likely word.                                                            |
| `top_a`              | `default` sends none. `custom` sends a value from 0 to 1; higher drops more unlikely words when one word is very likely.                                                                      |
| `frequency_penalty`  | `default` sends none. `custom` sends a value from -2 to 2; above 0, a word repeats less the more often it has appeared.                                                                       |
| `presence_penalty`   | `default` sends none. `custom` sends a value from -2 to 2; above 0, any word that has appeared repeats less.                                                                                  |
| `repetition_penalty` | `default` sends none. `custom` sends a value from 0 to 2; above 1, words from the prompt and the answer repeat less.                                                                          |
| `outputs`            | `text`, `image and text`, or `audio and text`. Images and audio need a model that makes them.                                                                                                 |
| `aspect_ratio`       | The shape of the images a model draws.                                                                                                                                                        |
| `voice`              | The voice of a spoken answer, such as `alloy`. Music models need it empty.                                                                                                                    |
| `pdf_engine`         | How OpenRouter reads PDFs: `native`, `cloudflare-ai`, or `mistral-ocr`. `default` uses the model's own file reading, or `mistral-ocr` when it has none.                                       |
| `seed`               | Varies the output, for models that take a seed.                                                                                                                                               |
| `run_number`         | Change this number to send the same request again.                                                                                                                                            |
| `json_schema`        | The `response_format.json_schema` object: a `name` and the `schema` the answer must follow, with `strict` if you want it. Only providers that follow it answer. Leave it empty for free text. |
| `stop`               | Text that ends the answer, one per line. Leave it empty to send none.                                                                                                                         |
| `prompt`             | The question or instruction.                                                                                                                                                                  |
| `conversation`       | Earlier turns, from another **Chat: Ask**.                                                                                                                                                    |
| `documents`          | Files from **Chat: Attach Document**.                                                                                                                                                         |
| `options`            | Settings from **Request Options**.                                                                                                                                                            |
| `system_prompt`      | The system prompt: instructions for the whole answer.                                                                                                                                         |

## Outputs

| Output         | What it carries                                                                         |
| -------------- | --------------------------------------------------------------------------------------- |
| `text`         | The answer, or the words of a spoken answer. Some drawing models return only images.    |
| `reasoning`    | The model's reasoning, if it shares it. Connected nodes are skipped when there is none. |
| `images`       | The images the model made. Connected nodes are skipped when it is empty.                |
| `audio`        | The spoken or musical answer. Connected nodes are skipped when it is empty.             |
| `conversation` | The earlier turns plus this question and answer, for the next **Chat: Ask**.            |

## Use

1. Write the prompt and type the model ID.
2. Connect any media the model reads.
3. Connect `text` to **Preview as Text**, and select **Run**.

Examples: **chat-01-write-a-product-listing** and
**chat-02-caption-a-training-set**.

Everything connected to `images`, `videos`, and `audio` goes in one
request: one item, a batch, a list such as `Load Image (from Folder)` makes,
or several **Load Image** nodes joined by **Create List**. Images keep their own
sizes.

Before you pay anything, the node refuses media the model does not read,
`outputs` it does not make, and a sampling setting or `stop` it does not take.
It also refuses a `json_schema` the model cannot follow, and `max_tokens` above
its longest answer. With
a sampling setting, `stop`, or `json_schema`, only providers that take every one
of them answer.

An answer that stops mid-sentence hit the token limit; raise `max_tokens`.

[OpenRouter multimodal documentation](https://openrouter.ai/docs/guides/overview/multimodal/overview)

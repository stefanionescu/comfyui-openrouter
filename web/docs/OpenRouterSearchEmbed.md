# Search: Embed

Turns lines of text and images into embeddings, and compares each one with the
first.

## Inputs

| Input        | What it takes                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------- |
| `model`      | Any embedding model ID from openrouter.ai/models; the default is `openai/text-embedding-3-small`. |
| `images`     | Images, for models that read them. Each image in a list or batch is one item.                     |
| `dimensions` | The embedding length, for models that can shorten it; 0 leaves it to the model.                   |
| `input_type` | Whether the items are queries or documents, for models that treat them differently.               |
| `run_number` | Change it to send the same request again.                                                         |
| `texts`      | One item per line. Blank lines are skipped.                                                       |
| `options`    | Settings from **Request Options**.                                                                |

## Outputs

| Output         | What it carries                                                            |
| -------------- | -------------------------------------------------------------------------- |
| `vectors`      | A JSON list with one embedding per item: the texts first, then the images. |
| `similarities` | A JSON list of each item's cosine similarity to the first item.            |

## Use

1. Write one item per line, with the item to compare against first.
2. Connect **similarities** to **Preview as Text**.
3. Select **Run**.

All items go in one request, up to 256, so the images from one **Image:
Generate** run are compared together. A model that reads only text refuses
images before anything is paid. Example:
**image-02-reject-distorted-images**.

[OpenRouter embeddings documentation](https://openrouter.ai/docs/api_reference/embeddings)

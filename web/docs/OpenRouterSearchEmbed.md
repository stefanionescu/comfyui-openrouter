# Search: Embed

Turn lines of text and images into embedding vectors, and compare each item with the first. Connect **similarities** to **Preview as Text**. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input          | What it takes                                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `texts`        | One item per line; blank lines are skipped.                                                                             |
| `model`        | Every OpenRouter embedding model; by default `openai/text-embedding-3-small`. Choose **other model ID** to type any ID. |
| `model.images` | Images, for a model that reads images; every image in a list or batch becomes one item.                                 |
| `dimensions`   | The vector length, for models that shorten vectors; 0 leaves it to the model.                                           |
| `input_type`   | A hint for models that embed queries and documents differently.                                                         |
| `variation`    | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed.             |
| `options`      | From **Request Options**, to choose providers.                                                                          |

## Outputs

| Output         | What it carries                                                                 |
| -------------- | ------------------------------------------------------------------------------- |
| `vectors`      | A JSON list with one vector per item: the texts first, then the images.         |
| `similarities` | A JSON list with each item's cosine similarity to the first item, which is 1.0. |

## Run

1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write one item per line, with the item to compare against first.
1. Select **Run**.

The node gathers every list that reaches it into one request, so the images of one **Image: Generate** run are compared together. At most 256 items go in one request.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter embeddings documentation](https://openrouter.ai/docs/api_reference/embeddings)

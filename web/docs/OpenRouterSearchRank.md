# Search: Rank

Order lines of text and images by how well they match a query, best first. Connect **texts** or **images** to the nodes that use the best matches. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input          | What it takes                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| `query`        | What the documents are ranked against.                                                                      |
| `documents`    | One document per line; blank lines are skipped.                                                             |
| `model`        | Every OpenRouter rank model; by default `cohere/rerank-v3.5`. Choose **other model ID** to type any ID.     |
| `model.images` | Images, for a multimodal rank model; every image in a list or batch becomes one document.                   |
| `top_n`        | How many documents to keep; 0 keeps all.                                                                    |
| `variation`    | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed. |
| `options`      | From **Request Options**, to choose providers.                                                              |

## Outputs

| Output   | What it carries                                                                                    |
| -------- | -------------------------------------------------------------------------------------------------- |
| `texts`  | The ranked text documents, one per line, best first.                                               |
| `images` | The ranked images as a list, best first; the nodes connected to it do not run when there are none. |
| `scores` | A JSON list of `index`, `kind`, and `score` for each ranked document, best first.                  |

## Run

1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write the query and the documents, and connect any images.
1. Select **Run**.

The node gathers every list that reaches it into one request, so ranking four images of one **Image: Generate** run costs one request. Only multimodal rank models take images.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter rerank documentation](https://openrouter.ai/docs/api/api-reference/rerank/submit-a-rerank-request)

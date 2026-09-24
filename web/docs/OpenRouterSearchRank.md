# Search: Rank

Ranks lines of text and images by how well they match a query, best first. Each
run is one paid request; prices are in **OpenRouter models**.

## Inputs

| Input          | What it takes                                                                                 |
| -------------- | --------------------------------------------------------------------------------------------- |
| `query`        | What to rank against.                                                                         |
| `documents`    | One document per line. Blank lines are skipped.                                               |
| `model`        | Any rank model; the default is `cohere/rerank-v3.5`. Choose **other model ID** to type an ID. |
| `model.images` | Images, for models that read them. Each image in a list or batch is one document.             |
| `top_n`        | How many results to keep; 0 keeps all.                                                        |
| `variation`    | **run number**: change it to send the same request again.                                     |
| `options`      | Settings from **Request Options**.                                                            |

## Outputs

| Output   | What it carries                                                              |
| -------- | ---------------------------------------------------------------------------- |
| `texts`  | The ranked text documents, one per line, best first.                         |
| `images` | The ranked images, best first. Connected nodes are skipped when it is empty. |
| `scores` | A JSON list of `index`, `kind`, and `score` for each result, best first.     |

## Use

1. Write the query and the documents, and connect any images.
2. Connect **texts** or **images** to the nodes that use the best results.
3. Select **Run**.

All documents go in one request, so ranking the four images of one **Image:
Generate** run costs one request. Examples:
**search-01-answer-from-help-articles** and **search-02-choose-a-hero-image**.

[OpenRouter rerank documentation](https://openrouter.ai/docs/api/api-reference/rerank/submit-a-rerank-request)

# Request Options

Choose providers, price caps, and extra request fields once, for any number of OpenRouter nodes. Connect **options** to the **options** socket of a paid node. It sends nothing itself.

## Inputs

| Input                  | What it takes                                                                                      |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| `order`                | Provider slugs to try first, in order, separated by commas.                                        |
| `only`                 | The only providers allowed.                                                                        |
| `ignore`               | Providers never used.                                                                              |
| `sort`                 | Prefer the cheapest (`price`), fastest (`throughput`), or quickest-to-answer (`latency`) provider. |
| `allow_fallbacks`      | Whether another provider may answer when the chosen ones cannot.                                   |
| `data_collection`      | `deny` to use only providers that do not store or train on requests.                               |
| `zdr`                  | Use only providers with zero data retention. Video cannot use it.                                  |
| `max_prompt_price`     | Skip providers above this input price in US dollars per million tokens; 0 sets no cap.             |
| `max_completion_price` | Skip providers above this output price in US dollars per million tokens; 0 sets no cap.            |
| `provider_options`     | A JSON object of fields for one provider, keyed by its slug.                                       |
| `extra_fields`         | A JSON object of request fields added to the body as written.                                      |

## Outputs

| Output    | What it carries                          |
| --------- | ---------------------------------------- |
| `options` | The options, for the **options** socket. |

## Run

1. To start from a finished workflow, open **chat-01-write-a-product-listing** from **Browse Templates → comfyui-openrouter**.
1. Fill in the fields you need and leave the rest at their defaults.
1. Connect **options** to the **options** socket of one or more paid nodes.

Each endpoint accepts only some fields, and a paid node refuses a field its endpoint does not accept before it sends anything:

| Field                           | Chat | Image | Video | Speech | Transcribe | Embed | Rank | Decision |
| ------------------------------- | ---- | ----- | ----- | ------ | ---------- | ----- | ---- | -------- |
| order, only, ignore             | Yes  | Yes   | No    | No     | No         | Yes   | Yes  | Yes      |
| sort, allow fallbacks           | Yes  | Yes   | No    | No     | No         | Yes   | Yes  | Yes      |
| data collection, zero retention | Yes  | No    | No    | No     | No         | Yes   | Yes  | Yes      |
| price caps                      | Yes  | No    | No    | No     | No         | Yes   | Yes  | Yes      |
| provider options                | Yes  | Yes   | Yes   | Yes    | Yes        | No    | No   | No       |

A node also refuses an extra field it sets itself, such as `model` or `messages`. Provider slugs and each provider's options are on the model's page on OpenRouter, linked from **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter provider selection documentation](https://openrouter.ai/docs/guides/routing/provider-selection)

# Request Options

Sets providers, price limits, and extra request fields for any number of paid
nodes.

## Inputs

| Input                  | What it takes                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------- |
| `provider`             | The one provider to use, as a slug; empty lets OpenRouter choose.                            |
| `only`                 | The only providers to use.                                                                   |
| `ignore`               | Providers never to use.                                                                      |
| `sort`                 | Prefer the cheapest (`price`), fastest (`throughput`), or quickest (`latency`) provider.     |
| `data_collection`      | `deny` to use only providers that do not store or train on requests.                         |
| `zdr`                  | Use only providers with zero data retention.                                                 |
| `max_prompt_price`     | Skip providers that charge more per million prompt tokens, in US dollars; 0 is no limit.     |
| `max_completion_price` | Skip providers that charge more per million completion tokens, in US dollars; 0 is no limit. |
| `provider_options`     | A JSON object of fields for one provider, keyed by its slug.                                 |
| `extra_fields`         | A JSON object of fields added to the request as written.                                     |

## Outputs

| Output    | What it carries                              |
| --------- | -------------------------------------------- |
| `options` | The settings, for a paid node's **options**. |

## Use

1. Fill in the fields you need, and leave the rest at their defaults.
2. Connect **options** to the **options** input of one or more paid nodes.

Which fields each request type accepts. A paid node stops with an error, before
sending, on a field its request type rejects:

| Field                                | Chat | Image | Video | Speech | Transcribe | Embed | Rank | Decision |
| ------------------------------------ | ---- | ----- | ----- | ------ | ---------- | ----- | ---- | -------- |
| provider, only, ignore               | Yes  | Yes   | No    | No     | No         | Yes   | Yes  | Yes      |
| sort                                 | Yes  | Yes   | No    | No     | No         | Yes   | Yes  | Yes      |
| data collection, zero data retention | Yes  | No    | No    | No     | No         | Yes   | Yes  | Yes      |
| price limits                         | Yes  | No    | No    | No     | No         | Yes   | Yes  | Yes      |
| provider options                     | Yes  | Yes   | Yes   | Yes    | Yes        | Yes   | Yes  | Yes      |

Each request goes to one provider, and OpenRouter never moves it to another. A
node also refuses an extra field it sets itself, such as `model`, `messages`, or
`provider`. **Model: Info** lists a model's provider slugs, and each model's page
at openrouter.ai/models lists their options. Example: **chat-01-write-a-product-listing**.

[OpenRouter provider selection documentation](https://openrouter.ai/docs/guides/routing/provider-selection)

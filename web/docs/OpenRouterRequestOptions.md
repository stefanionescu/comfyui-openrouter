# Request Options

Sets providers, price limits, and extra request fields for any number of paid
nodes.

## Inputs

| Input                  | What it takes                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------- |
| `order`                | Providers to try first, in this order, as slugs separated by commas.                         |
| `only`                 | The only providers to use.                                                                   |
| `ignore`               | Providers never to use.                                                                      |
| `sort`                 | Prefer the cheapest (`price`), fastest (`throughput`), or quickest (`latency`) provider.     |
| `allow_fallbacks`      | Whether another provider may answer when the chosen ones cannot.                             |
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
| order, only, ignore                  | Yes  | Yes   | No    | No     | No         | Yes   | Yes  | Yes      |
| sort, allow fallbacks                | Yes  | Yes   | No    | No     | No         | Yes   | Yes  | Yes      |
| data collection, zero data retention | Yes  | No    | No    | No     | No         | Yes   | Yes  | Yes      |
| price limits                         | Yes  | No    | No    | No     | No         | Yes   | Yes  | Yes      |
| provider options                     | Yes  | Yes   | Yes   | Yes    | Yes        | No    | No   | No       |

A node also refuses an extra field it sets itself, such as `model` or
`messages`. Provider slugs and their options are on each model's page at
openrouter.ai/models. Example:
**chat-01-write-a-product-listing**.

[OpenRouter provider selection documentation](https://openrouter.ai/docs/guides/routing/provider-selection)

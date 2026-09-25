# Model: Info

Shows what an OpenRouter model reads, makes, and accepts, as JSON. It reads
OpenRouter's public listings, so it is free and needs no key.

## Inputs

| Input   | What it takes                                                                     |
| ------- | --------------------------------------------------------------------------------- |
| `model` | Any model ID from openrouter.ai/models; the default is `google/gemini-3.5-flash`. |

## Outputs

| Output | What it carries                                          |
| ------ | -------------------------------------------------------- |
| `info` | The model's listing as JSON, with the keys listed below. |

The paid nodes check each request against the same listings before paying, so
**info** holds exactly what they accept.

| Key                   | What it holds                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------- |
| model                 | The model ID.                                                                             |
| inputs                | What the model reads, such as `text`, `image`, `audio`, or `video`.                       |
| outputs               | What the model makes, such as `text`, `image`, `video`, `speech`, or `embeddings`.        |
| context_length        | The most tokens any provider reads, or `null` when none says.                             |
| max_completion_tokens | The longest answer any provider gives, or `null` when none says.                          |
| parameters            | The chat request fields at least one provider accepts, such as `seed` or `reasoning`.     |
| voice_cloning         | Whether a provider copies a voice from a sample.                                          |
| providers             | The provider slugs **Request Options** takes, such as `google-vertex`.                    |
| fields                | The image or video fields the model takes. `{}` for a model that makes no image or video. |

In `fields`, a field with fixed values holds `values`, a number holds `min` and
`max`, and a field that is only on or off holds `{}`. For example:
`{"aspect_ratio": {"values": ["1:1", "16:9"]}, "n": {"min": 1, "max": 4}, "seed": {}}`.

## Use

1. Type or connect the model ID.
2. Connect **info** to **Preview as Text** to read it, or to **Extract Text from
   JSON** to use one top-level key.

Another extension can run the node and read **info** instead of copying a
model's limits; the advanced guide explains how. Examples:
**image-04-design-a-logo** and **video-01-animate-a-product-shot**.

[OpenRouter models documentation](https://openrouter.ai/docs/guides/overview/models)

# Decision: Ask

Asks a decision model, such as Jev, questions about a situation, and returns
the answers with their probabilities. Each run is one paid request; Jev bills only
the input, and prices are in **OpenRouter models**.

## Inputs

| Input       | What it takes                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------ |
| `situation` | What to decide on, up to 200,000 characters. A JSON object or array is sent as JSON.             |
| `questions` | The questions, from **Decision: Add Question**.                                                  |
| `model`     | Any decision model; the default is `typesafe/jev-1.13`. Choose **other model ID** to type an ID. |
| `variation` | **run number**: change it to send the same request again.                                        |
| `options`   | Settings from **Request Options**.                                                               |

## Outputs

| Output    | What it carries                                                  |
| --------- | ---------------------------------------------------------------- |
| `answers` | Every answer, for **Decision: Read Answer**.                     |
| `summary` | One line per answer, such as `team: payments (confidence 0.75)`. |

## Use

1. Write the situation and connect the questions.
2. Connect **answers** to **Decision: Read Answer**, and **summary** to
   **Preview as Text**.
3. Select **Run**.

Examples: **decision-01-verify-then-escalate** and
**audio-01-triage-a-voicemail**. The default model is a fixed version, as
OpenRouter recommends when you tune thresholds.

This node uses OpenRouter's alpha decisions API (`/api/alpha/decisions`),
which OpenRouter may still change.

[OpenRouter Jev documentation](https://openrouter.ai/docs/guides/community/jev)

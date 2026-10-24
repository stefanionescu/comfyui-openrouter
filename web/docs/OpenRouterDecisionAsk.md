# Decision: Ask

Asks a decision model on OpenRouter, such as TypeSafe's Jev, typed questions
about a situation. Each answer comes with its probabilities.

## Inputs

| Input        | What it takes                                                                                       |
| ------------ | --------------------------------------------------------------------------------------------------- |
| `questions`  | The questions, from **Decision: Add Question**.                                                     |
| `model`      | Any decision model ID from openrouter.ai/models; the default is at openrouter.ai/typesafe/jev-1.13. |
| `run_number` | Change it to send the same request again.                                                           |
| `situation`  | What to decide on, within what the model reads. A JSON object or array is sent as JSON.             |
| `options`    | Settings from **Request Options**.                                                                  |

## Outputs

| Output    | What it carries                                                  |
| --------- | ---------------------------------------------------------------- |
| `answers` | Every answer, for **Decision: Read Answer**.                     |
| `summary` | One line per answer, such as `team: payments (confidence 0.75)`. |

## Use

1. Write the situation and connect the questions.
2. Connect `answers` to **Decision: Read Answer**, and `summary` to
   **Preview as Text**.
3. Select **Run**.

Examples: **decision-01-verify-then-escalate** and
**audio-01-triage-a-voicemail**.

The default model is a fixed version of Jev. To follow TypeSafe's
newest release, type `~typesafe/jev-latest` in `model`. **Model: Info** shows
how many tokens a model reads, as `context_length`.

This node uses the alpha decisions API of OpenRouter, `/api/alpha/decisions`,
which OpenRouter may still change.

[OpenRouter Jev documentation](https://openrouter.ai/docs/guides/community/jev)

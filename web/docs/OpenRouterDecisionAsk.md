# Decision: Ask

Answer typed questions about a situation with an OpenRouter decision model, such as Jev. It answers with probabilities instead of text. Connect **answers** to **Decision: Read Answer** and **summary** to **Preview as Text**. Each run sends one paid OpenRouter request with your OpenRouter key.

## Inputs

| Input       | What it takes                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------- |
| `situation` | What to decide on. A JSON object or array is sent as JSON; anything else as text.                           |
| `questions` | The questions, from **Decision: Add Question**.                                                             |
| `model`     | Every OpenRouter decision model; by default `typesafe/jev-1.13`. Choose **other model ID** to type any ID.  |
| `variation` | The **run number**. Change this number to send the request again with unchanged inputs. Each run is billed. |
| `options`   | From **Request Options**, to choose providers.                                                              |

## Outputs

| Output    | What it carries                                                  |
| --------- | ---------------------------------------------------------------- |
| `answers` | Every answer, for **Decision: Read Answer**.                     |
| `summary` | One line per answer, such as `team: payments (confidence 0.75)`. |

## Run

1. To start from a finished workflow, open **decision-01-verify-then-escalate** or **audio-01-triage-a-voicemail** from **Browse Templates → comfyui-openrouter**.
1. Set your key in **ComfyUI menu → Extensions → OpenRouter → OpenRouter settings**.
1. Write the situation and connect the questions.
1. Select **Run**.

Jev's output tokens are free, so a run costs only its input. The default model is pinned to a version, because OpenRouter recommends pinning one when you tune thresholds. The situation must fit in 200,000 characters.

This node uses OpenRouter's alpha decisions API. OpenRouter can change it without notice, and a change can stop the node until the extension is updated. Jev's answers are probabilities: review the decisions that matter before you act on them.

For current prices, open **Extensions → OpenRouter → OpenRouter models**.

[OpenRouter Jev documentation](https://openrouter.ai/docs/guides/community/jev)

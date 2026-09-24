# Decision: Add Question

Add one question for a decision model. Its **answer type** shows only the fields that type needs. Chain several of these nodes to ask several questions, then connect the last one to **Decision: Ask**. It sends nothing to OpenRouter.

## Inputs

| Input                   | What it takes                                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `questions`             | The earlier questions, from another **Decision: Add Question**; up to 32 in one decision.                              |
| `name`                  | Lowercase letters, digits, and underscores, starting with a letter; each question needs its own name.                  |
| `instructions`          | What the question asks.                                                                                                |
| `answer_type`           | **yes or no** for a probability of yes, **one choice** to pick one option, or **score** for a place on ordered levels. |
| `answer_type.yes_means` | When the answer is yes. Describe both yes and no, or neither.                                                          |
| `answer_type.no_means`  | When the answer is no.                                                                                                 |
| `answer_type.options`   | One option per line, as `key: description`; a line without a colon is a key with no description. 2 to 32 options.      |
| `answer_type.levels`    | One level per line, lowest first; 2 to 11 levels.                                                                      |

## Outputs

| Output      | What it carries                                       |
| ----------- | ----------------------------------------------------- |
| `questions` | The earlier questions with this one added at the end. |

## Run

1. Name the question and write what it asks.
1. Choose the answer type and fill in its fields.
1. Connect **questions** to the next question or to **Decision: Ask**.

Use **yes or no** for checks, such as whether an image matches its brief; **one choice** to route or classify, such as which team handles a ticket; and **score** for a degree, such as urgency. A score answer runs from 0 to the number of levels minus one.

[OpenRouter Jev documentation](https://openrouter.ai/docs/guides/community/jev)

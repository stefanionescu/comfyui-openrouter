# Decision: Add Question

Adds one question for **Decision: Ask**. Chain several of these nodes to ask
several questions.

## Inputs

| Input                   | What it takes                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------- |
| `questions`             | Questions from another **Decision: Add Question**. One decision takes up to 32.       |
| `name`                  | A unique name: lowercase letters, digits, and underscores, starting with a letter.    |
| `instructions`          | The question.                                                                         |
| `answer_type`           | **yes or no**, **one choice** from a list of options, or **score** on ordered levels. |
| `answer_type.yes_means` | What yes means. Describe both yes and no, or neither.                                 |
| `answer_type.no_means`  | What no means.                                                                        |
| `answer_type.options`   | 2 to 32 options, one per line, as `key: description`. The description is optional.    |
| `answer_type.levels`    | 2 to 10 levels, one per line, lowest first.                                           |

## Outputs

| Output      | What it carries                      |
| ----------- | ------------------------------------ |
| `questions` | The earlier questions plus this one. |

## Use

1. Name the question and write it.
2. Choose the answer type and fill in its fields.
3. Connect **questions** to the next question, or to **Decision: Ask**.

Use **yes or no** for a check, such as whether an image matches its brief;
**one choice** to classify, such as which team handles a ticket; and **score**
for a degree, such as urgency. A score runs from 0 to the number of levels minus
one. Examples: **audio-01-triage-a-voicemail** and
**image-01-pick-the-best-image-for-an-occasion**.

[OpenRouter Jev documentation](https://openrouter.ai/docs/guides/community/jev)

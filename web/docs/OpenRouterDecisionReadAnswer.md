# Decision: Read Answer

Reads one answer from **Decision: Ask**, by its question's name, as text, a yes
flag, and numbers.

## Inputs

| Input       | What it takes                                              |
| ----------- | ---------------------------------------------------------- |
| `answers`   | The answers, from **Decision: Ask**.                       |
| `question`  | The name of the question to read.                          |
| `threshold` | The probability or confidence at which **is_yes** is true. |

## Outputs

| Output        | What it carries                          |
| ------------- | ---------------------------------------- |
| `answer`      | The answer as text.                      |
| `is_yes`      | Whether the answer passes the threshold. |
| `probability` | The probability of the answer.           |
| `score`       | The answer as a number.                  |
| `level`       | The answer's position, from 0.           |
| `confidence`  | How sure the model is.                   |

Each output has a value for every answer type:

| Output      | One choice                         | Yes or no                          | Score                             |
| ----------- | ---------------------------------- | ---------------------------------- | --------------------------------- |
| answer      | The chosen key                     | `yes` or `no` at the threshold     | The text of the nearest level     |
| is_yes      | Confidence at least the threshold  | Probability at least the threshold | Confidence at least the threshold |
| probability | Probability of the chosen key      | Probability of yes                 | Probability of the nearest level  |
| score       | Probability of the chosen key      | Probability of yes                 | The score                         |
| level       | Position of the chosen key, from 0 | 1 for yes, 0 for no                | The nearest level, from 0         |
| confidence  | Confidence                         | The larger of p and 1 minus p      | Confidence                        |

## Use

1. Connect **answers** from **Decision: Ask**.
2. Type the question's name, and set the threshold.
3. Connect the output you need, such as **is_yes** to **If/Else Switch**.

Examples: **image-03-edit-with-the-best-idea** and
**decision-01-verify-then-escalate**.

[OpenRouter Jev documentation](https://openrouter.ai/docs/guides/community/jev)

# Creating Plans

These rules apply whenever an agent creates any implementation plan, refactor
plan, documentation plan, data change plan, workflow plan, script plan, or
other planned change sequence.

## Contents

- [Concrete change descriptions](#concrete-change-descriptions)
- [No automated tests or unrequested checks](#no-automated-tests-or-unrequested-checks)
- [Implementation order](#implementation-order)
- [Plan detail level](#plan-detail-level)

## Concrete change descriptions

A plan must identify every change it proposes at the level needed to settle
real implementation decisions. Scale the detail to the change; a small edit
does not need the machinery of a multi-stage migration.

Rules:

- Identify the affected files, declarations, configuration keys, and behavior.
- Include short code or text examples only when they resolve an implementation
  decision that names and prose cannot express clearly.
- Identify new and deleted files and explain their purpose.
- Include exact commands or tool operations when their arguments determine the
  result, safety, or reproducibility. Routine text edits do not need a transcript
  of editor operations.
- Include changes to generated files when the plan expects generated files to
  change.
- For generated results, binary assets, and other non-text artifacts, list the
  exact source path, output path, and operation.
- For those artifacts, include dimensions or metadata changes when relevant
  and the command or tool needed to reproduce the result.

## No automated tests or unrequested checks

Follow [GENERAL.md](GENERAL.md#verification-scope). Do not include automated
test files or test commands in plans. Include other verification only within
the explicitly requested scope.

## Implementation order

Plans must define the implementation order where steps depend on one another.
Identify independent steps without inventing an ordering dependency.

Rules:

- Break the work into sequential steps.
- Put dependency discovery before edits that depend on that discovery.
- Put shared contract or type changes before callers that use them.
- Put data shape changes before runtime, workflow, or publishing surfaces that consume the data.
- Put ownership moves before import or call-site updates.
- Put generated output after the source change that produces it.
- Put cleanup after all call sites have moved.
- Keep each step concrete enough that another agent can execute it without
  inventing missing decisions.
- State which files, symbols, assets, commands, and behavior belong to each step.
- Do not hide multiple unrelated edits inside one broad step.

Bad:

```text
1. Refactor the loader.
2. Update the workflow command.
```

Good:

```text
1. Add the named `ModelSettings` field and define its value source.
2. Update `build_settings` to populate the field.
3. Replace the identified runtime and workflow call sites.
4. Remove the named derived-value helper after its callers move.
```

## Plan detail level

Plans must explain the intended changes clearly enough to implement.

Rules:

- Include the reasoning needed to understand why the steps are ordered that way.
- Use the concrete file, declaration, configuration, and artifact details
  specified in [concrete change descriptions](#concrete-change-descriptions).
  State them once in the step that owns the change.
- Include expected intermediate states when a sequence temporarily changes
  contracts, generated outputs, or asset files.
- Include all constraints, assumptions, and dependencies that affect execution.
- Include edge cases or failure modes only when they are part of the real
  requested work.
- Do not leave placeholders such as "update as needed", "adjust imports", or
  "fix any errors".
- State the required behavior, contracts, commands, and asset operations. Leave
  routine coding details to implementation.

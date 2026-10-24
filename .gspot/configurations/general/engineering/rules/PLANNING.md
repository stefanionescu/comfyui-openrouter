# Planning

Read this rule before you write a plan.

## Complete change content

A plan holds the complete content of every change it proposes, so another agent can carry it out without inventing
anything.

- Show the exact diff of each code, configuration, documentation, schema, and text change, and the full contents of
  every new file. Do not summarize a change the diff can show.
- Name every command that creates, moves, renames, regenerates, or deletes a file. List each generated file the change
  rewrites.
- For an image or another binary file, give the source and output paths, the operation, and the command that reproduces
  it.
- Leave no placeholder such as `update accordingly`, `adjust imports`, or `fix any errors`.

Bad:

```text
Update the settings screen copy.
```

Good:

```diff
--- a/app/settings/page.tsx
+++ b/app/settings/page.tsx
-<h1>Old title</h1>
+<h1>Account settings</h1>
```

## Order and detail

One step holds one change. Order the steps so each one builds on finished work. Change a shared interface before its
callers. Move a module before the imports that point at it. Put generated output after the source that produces it, and
cleanup after the last caller.

Say why the steps run in that order, and name the constraints and assumptions that affect them. Mention an edge case
only when it belongs to the requested work.

## Verification steps

End the plan with the commands that prove the change works, and what each one prints when it passes. Run only the checks
that cover the change, as WORKING.md says.

# YAML

Read this rule when you change a `.yml` or `.yaml` file.

- Keep one document per file unless the consumer requires a stream.
- Quote a string value that YAML otherwise reads as another type: `yes`, `no`, `on`, `off`, `null`, `~`, a version such
  as `1.10`, an octal-looking number, and text that starts with `*`, `&`, `!`, `%`, `@`, or a backtick.
- Name each anchor for what it holds, such as `&checkout-options`. Do not keep a name that a tool generated, such as
  `&a1`.
- Do not use merge keys, `<<:`. YAML 1.2 does not define them, and some readers ignore them.
- Write a long string as a block scalar, `|` or `>`, not as a quoted string with escapes.

## Comments

- Put a comment that describes the whole file at the top, above the first key. Do not put it after `name:` or between
  two top-level keys.
- Put a comment about one key on the line above it, at the same indentation.
- Do not add a comment at the end of a line. Allow a version comment only after a pinned commit, such as
  `uses: jdx/mise-action@<sha> # v5.1.1`.
- When the format has a description field, such as `description` in `action.yml`, put the text there, not in a comment.

## Organization

- Order keys as the consumer documents them, then alphabetically. Reorder keys only in a file that you also change for
  another reason.
- Use the `.yml` extension. Keep a file name that a tool requires, such as `compose.yaml` or `pnpm-workspace.yaml`.

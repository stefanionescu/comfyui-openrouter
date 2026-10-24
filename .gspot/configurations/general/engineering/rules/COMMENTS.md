# Comments

Read this rule when you write or change a comment.

## What a comment says

A comment explains why, not what, and describes the code in its current form.

Bad: `# Removed the old cache loader.` Good: `# The provider allows 100 requests an hour, so read the cache first.`

## When to comment

Write the doc comments that the checks of the language require. Say what the signature does not. Never write a comment
that only repeats a name or a type. Add other comments only when a function:

- handles a failure that its public interface does not explain
- has concurrency, cancellation, or isolation requirements
- makes a security or privacy decision
- encodes a domain invariant such as `idempotent` or `retry-safe`
- sits on a hot path
- takes more than ten seconds to understand from its signature and body

## Keep comments true

When you change a function, update its doc comment: summary, parameters, what it returns when the type does not say it,
and errors. Rewrite or delete a comment that describes behavior the code lacks, or the reason for a decision you undo.

- When you move or delete a declaration, do the same to its comment. A doc comment sits directly above its declaration,
  with no blank line between them.
- Use a file header only when it helps the reader. When present, the header describes the whole file in a single
  sentence. Update it when the file's job changes.
- Do not write work status in a comment. For example, do not describe a paused job or a temporary choice.
- Never copy a size, time, or default from the code into a comment; name the constant.

## Deferred work

Track unfinished work in the issue tracker. Do not leave `TODO`, `FIXME`, `XXX`, or `HACK` in comments. An issue link
may explain an existing constraint, never promise a later implementation.

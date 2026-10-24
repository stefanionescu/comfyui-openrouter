# Errors

Read this rule when you write code that raises, catches, or reports an error.

## Error taxonomy

- Return a typed result or throw a typed error for an expected operational failure. Invalid input, missing resources,
  denied permission, and provider timeouts need results the caller can act on.
- Never catch a programmer error, such as a broken invariant, to keep going. Log its stack and show a generic failure.
- A startup failure stops the process before it accepts work.
- On shutdown, set readiness to false, stop accepting work, drain in-flight work for a bounded time, close resources,
  and exit.
- A fatal runtime error stops new work, reports the failure, and exits. Last-resort handlers never keep serving.

## Raising and catching

- Catch the narrowest type. Never a bare catch-all unless the block re-raises or deliberately isolates an operation and
  records the failure.
- Keep the try block around the one operation that can fail.
- Preserve the cause when wrapping: `new Error(message, { cause })`, `raise ... from error`, or `Error` conformance with
  an underlying error.
- Do not swallow failures. Handle, record, or re-raise each caught error.
- Run required cleanup in `finally` or the language's equivalent.
- Check the `error` field of an SDK that returns `{ data, error }`, such as Supabase, before using `data`.

## Async work

- Capture the identity of the resource when async work starts. A late result never overwrites a newer resource or
  another session.
- Retry a write only when the operation has an idempotency key.

## Error messages

A developer tool may name the file, line, and setting that the user must fix. Keep unrelated private data out of every
output.

**Keep out of public service responses:**

- Schema names, table names, column names, or function names.
- Internal identifiers such as row IDs, user IDs, or session tokens.
- Stack traces or file paths.
- Raw upstream, provider, or database errors.
- Implementation details such as trigger and policy names, or internal state like "deleted" flags.

**Always:**

- Make messages actionable: tell the user what went wrong, not how the system works.
- Put the failing value in its own field, not in the message text.
- Keep message text stable so readers can search for it.
- Convert technical errors to user-facing messages in the code that displays them.

## Message style

Use sentence case for error messages. Keep their tone and casing consistent across the repository. Preserve diagnostic
text from external tools when callers depend on its exact form.

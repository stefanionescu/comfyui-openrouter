# How to Work in This Repository

These rules apply to all files in this repository.

An owner is the module responsible for a behavior. A contract defines the inputs,
outputs, and behavior that callers rely on. A boundary receives data or commands
from another component, process, or service.

## Contents

- [Thinking before coding](#thinking-before-coding)
- [Scope discipline](#scope-discipline)
- [Handle real failure modes](#handle-real-failure-modes)
- [Keep one implementation](#keep-one-implementation)
- [Naming](#naming)
- [Abstractions](#abstractions)
    - [Prefer duplication over the wrong abstraction](#prefer-duplication-over-the-wrong-abstraction)
    - [Extract meaningful operations](#extract-meaningful-operations)
    - [Keep unrelated behavior separate](#keep-unrelated-behavior-separate)
    - [Inline the wrong abstraction](#inline-the-wrong-abstraction)
    - [Make the change easy](#make-the-change-easy)
    - [Keep operations easy to combine](#keep-operations-easy-to-combine)
    - [Pass dependencies when needed](#pass-dependencies-when-needed)
    - [Prefer data flow and data structures](#prefer-data-flow-and-data-structures)
- [Secrets and sensitive data](#secrets-and-sensitive-data)
- [Logging](#logging)
- [Error messages](#error-messages)
- [Verification scope](#verification-scope)
- [Verification commands](#verification-commands)
- [Code style](#code-style)
    - [Present state only](#present-state-only)
    - [Avoid referencing specific file paths](#avoid-referencing-specific-file-paths)
    - [Punctuation](#punctuation)
    - [Table of contents](#table-of-contents)
    - [Comments](#comments)
    - [Documentation requirements](#documentation-requirements)
    - [Documentation maintenance](#documentation-maintenance)
- [Protected files](#protected-files)
- [Language discipline](#language-discipline)
- [No backward compatibility](#no-backward-compatibility)
- [Working with uncommitted changes](#working-with-uncommitted-changes)

## Thinking before coding

Read the relevant code before touching it. Understand the contracts, data flow,
and ownership boundaries. Then think through your approach:

- What is the simplest change that solves the problem correctly?
- What are the failure modes? What happens with bad input, missing data, concurrent access, network failures?
- Does this change affect other parts of the system? Trace the call chain.
- Will someone reading this code in six months understand what it does and why?

When you rename or move a file, audit the entire codebase for references and
update them immediately. Stale imports and broken references are worse than the
original problem.

Before adding a new module, directory, or helper, identify the correct owner for
the behavior. Do not create parallel implementations for a concept that has an
owner. If a new file is needed, be ready to explain why that file belongs with
the owning module.

## Scope discipline

- Do what was asked. Do not expand scope.
- Report unrelated findings without adding them to the task.
- Do not add features, refactor surrounding code, or "improve" things that were not requested.

## Handle real failure modes

Do not invent defensive logic for scenarios that are not part of the real contract.

- Do not add guards, fallbacks, retries, optional handling, defaults, or wrappers
  for states that cannot occur under the real contract.
- Handle known failure modes at real boundaries: user input, network calls,
  persistence, permissions, and external services.
- Trust internal invariants after they are established. If an invariant is
  unclear, trace the code and clarify the contract instead of adding speculative
  protection.
- Do not pad the codebase with logic meant to protect against hypothetical future failures.

## Keep one implementation

Keep one clear implementation for each concept.

- Do not create multiple functions, services, types, or wrappers that do nearly the same thing.
- Put validation, policy, and transformations in the module that owns the operation.
  Do not add forwarding wrappers.
- Do not add forwarding layers or abstractions solely for hypothetical reuse.
  Extract a meaningful operation when its name, contract, or ownership makes
  the calling code clearer, even when it has one caller.
- Before adding a new helper, find the owner of the behavior and put the logic
  there.
- When touching duplicated logic in the same area, collapse it into the owner
  instead of adding another layer.

## Naming

Name files, directories, and declarations for what they do. Use consistent domain
terms and the casing required by the language. Keep required host API names exact.
Follow the configured naming, folder, file-size, function-size, and import-spacing
policies.
Keep a blank line after the complete import block, including before comments.

## Abstractions

Abstractions are useful only when they remove real complexity. They are harmful
when they hide ownership, combine unrelated behavior, or predict reuse before
the code proves it.

### Prefer duplication over the wrong abstraction

- Duplication is cheaper than the wrong abstraction.
- Prefer duplication until there are at least two real examples that prove the
  same concept exists.
- Do not build reusable code before the code is usable.
- Do not preserve an abstraction because of sunk cost.

### Extract meaningful operations

- A single caller does not justify an abstraction by itself. A helper must own
  a meaningful operation, invariant, resource lifetime, or external boundary;
  merely forwarding arguments does not qualify.
- Do not introduce an abstraction for hypothetical future reuse.

### Keep unrelated behavior separate

- If a shared abstraction starts gaining flags, modes, optional branches, or
  caller-specific conditionals, treat that as evidence the abstraction is wrong.
- Do not combine unrelated behavior in one function, class, or module and use
  flags to choose between it. Give each behavior a clear owner.

### Inline the wrong abstraction

- When an abstraction is wrong, inline it back into each caller, delete the
  branches each caller does not need, then extract only the common behavior that
  remains.

### Make the change easy

- Preparatory refactoring is allowed when it makes the requested change easier:
  first preserve behavior, then make the behavior change.
- Keep refactoring and behavior changes separate when practical.

### Keep operations easy to combine

- Let callers use the operations they need directly. Avoid APIs that force a
  caller to choose between one large operation and duplicating its internals.

### Pass dependencies when needed

- Let callers pass a dependency when existing callers need different behavior.
- Do not add factories or dependency-injection layers for hypothetical callers.

### Prefer data flow and data structures

- Prefer plain functions and explicit data flow before classes, interfaces,
  factories, strategies, inheritance, or framework patterns.
- Prefer data structures and their relationships over code-pattern taxonomies.
- Push state and I/O outward where practical; keep core logic pure or close to
  pure when that reduces moving parts.

## Secrets and sensitive data

- Never hardcode API keys, tokens, passwords, or secrets anywhere in the codebase.
- Never log sensitive data, including tokens, passwords, personal information,
  or request bodies with authentication headers.
- Use environment variables or the private credential store for secrets. Access
  them through the configuration boundary, not directly in node or browser code.

## Logging

Do not add logging to project-owned code, scripts, or configuration. This applies
at every severity level, including private development and diagnostic logging.
Do not create loggers, logging wrappers, log files, logging handlers, or logging
configuration. Do not substitute console calls, print statements, or shell
tracing for logging. Do not emit stack traces.

Return results and propagate failures through the operation's defined contract.
CLI commands may write their intended results to stdout and concise actionable
errors, required prompts, or user-requested status to stderr. This output must
serve the command's user-facing contract; it must not become a diagnostic event
stream. Local checks may report the locations needed to fix findings under the
error-message rules below. Existing third-party output does not authorize adding
project-owned logging.

## Error messages

Error messages visible to users, command-line callers, or interface help
must not leak internal system details.

These restrictions apply to runtime and user-facing output. Local development
checks may report source paths, line numbers, declaration names, and rule
identifiers needed to locate a failure. Keep credentials and private account
values out of all diagnostics.

**Never include in error messages:**

- Schema names, table names, column names, or function names
- Internal identifiers (row IDs, user IDs, session tokens)
- Stack traces or file paths
- Implementation details (trigger names, policy names, internal state like "deleted" flags)

**Always:**

- Start error messages with an uppercase letter (sentence case)
- Make messages actionable: tell the user what went wrong, not how the system works
- Use generic messages for configuration and infrastructure failures
- Keep messages consistent in tone and casing across the repository

## Verification scope

Do not create or run automated tests, or recreate deleted test files.
Run formatting, linting, type checks, builds, dependency checks, security scans,
and browser or manual checks only when the user explicitly requests them.
An implementation or documentation change does not itself request verification.

Use the existing local tools when checks are requested. Do not add hosted Git
workflows or deployment tooling.

## Verification commands

When verification is requested, use the existing command for the affected files
or behavior. Do not expand it to unrelated areas or reference projects. Report
what ran, what failed, and what was not checked.

For requested runtime checks, use the actual installed distribution in its
supported runtime. Source inspection and static checks do not prove that the
application or workflow runs.

## Code style

### Present state only

Comments and documentation describe what the code does now. Never mention what
was removed, deleted, renamed, or refactored, or how the code used to work. Do
not put changelogs in comments.

Bad: `# Replaced the old recording download.`
Good: `# Reject redirects before downloading a recording.`

### Avoid referencing specific file paths

Do not narrate source locations in comments. Keep file paths in commands, links,
and procedures when readers need them to complete the task.

Exceptions: well-known configuration files such as `pyproject.toml`,
`uv.lock`, and `dev dependency group` may be mentioned by name when
useful for the task.

### Punctuation

Do not use em dashes or double hyphens as prose punctuation. Use a space, comma,
or colon instead. Keep double hyphens when exact syntax requires them, such as
command options and suppression directives.

Bad: `The server handles requests - including retries - before responding.`
Good: `The server handles requests, including retries, before responding.`

### Table of contents

Long documentation files use a `## Contents` section with accurate anchor links
to the sections readers need most. Keep it current when headings change.

### Comments

Keep comments concise and focused on intent ("why"), not narration ("what"). Do
not put default values in comments because they drift when code changes. Refer
to concept names, not file paths.

Comments and doc comments must not contain these details unless a rule requires
them for a tool or the reference is essential for understanding:

- **Code change history.** No "changed X to Y", "replaced old Z", "updated to
  use W", or "refactored from". Git tracks history.
- **What was done to variables or code.** No "added this field", "moved this
  constant", or "renamed from oldName". Describe the present purpose.
- **File or variable locations.** Do not say "defined in X.ts" or "see the value
  in config.Y" without that concrete need. Code is searchable; stale path
  references are not.

Good doc comments describe what a function does, what its parameters mean, and
what it returns. They do not narrate how the function came to exist or what it
replaced.

### Documentation requirements

Doc comments are required where they clarify public behavior, non-obvious
contracts, or example and model boundaries. Keep the existing comment and
docstring requirements. Explain constraints that names and types cannot express.

#### Required comments

Keep Python docstrings required by the configured documentation coverage and
the function summaries required by the Bash guide. Coverage requirements still
apply to obvious or private declarations; they do not require filler. State the
operation's purpose or contract concisely. Do not paraphrase each statement,
repeat the signature, or add empty sections. Add details only when they explain
behavior that names and types do not express.

#### Always comment

Regardless of language or visibility, add a comment when a function:

- Handles edge cases or non-obvious failure modes.
- Has concurrency, cancellation, or isolation requirements.
- Makes security or privacy decisions.
- Encodes domain invariants ("must be monotonic", "idempotent", "retry-safe").
- Sits on a performance-sensitive hot path.
- Would take a reader more than ten seconds to understand from the signature and body alone.

Explain the reason for the behavior. A separate reviewer is not required.

### Documentation maintenance

Update comments and docstrings affected by the change. Remove statements that
are no longer true; do not expand the task into unrelated documentation cleanup.

Specific expectations:

- If you change a function's behavior, update its doc comment to match.
- If you change a function's parameters, update `@param` tags.
- If you change what a function returns, update `@returns`.
- If a comment references behavior that no longer exists, rewrite or remove it.
- If a comment describes the "why" of a decision you are undoing, remove it.

This applies to Python docstrings, Bash comments, Markdown documentation,
TypeScript JSDoc, node help, and workflow notes.

## Protected files

Do not modify `AGENTS.md` or files under `rules/` unless the user explicitly
asks for rule changes.

## Language discipline

Write text that readers can find, understand, and use for their task.

Use direct, concrete language in code, comments, filenames, and documentation.

- Name model adapters for the model and the operation they perform.
- Describe optional conditions explicitly.
- State the actual probability or condition instead of using vague hedging.
- Describe redundancy directly instead of using idioms.

If code uses vague language, improve it when touching that code.

## No backward compatibility

Do not add compatibility layers, forwarding wrappers, aliases for renamed
symbols, or deprecated implementations. Replace the old interface directly.

When something is replaced or renamed:

- Delete the old implementation entirely.
- Update every call site to use the new version.
- Remove unused files, functions, types, and variables.

Keep only the current implementation. For a requested rename or replacement,
update affected callers, schemas, examples, and stored data together. Migrate
required stored data directly; do not retain old IDs, aliases, forwarding
wrappers, dual paths, or deprecated implementations.

Keep names imposed by current framework and external APIs exact. Protect user
documents, saved workflows, media, and credentials. Do not discard user data
to avoid a migration.

## Working with uncommitted changes

When `git status` or the worktree shows changes you did not make, do not panic.
Other agents or contributors may be working in parallel.

- Do not revert, stash, clean, or overwrite changes you did not make.
- Continue when your changes do not conflict with existing work.
- Ask only when the requested change conflicts with existing work and you cannot
  determine how to complete it without overwriting that work.
- Build on top of uncommitted changes without altering unrelated changes.
- If another agent is known to be committing those changes separately, leave them alone.

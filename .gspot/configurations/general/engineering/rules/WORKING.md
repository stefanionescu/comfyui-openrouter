# Working in a Repository

Read this rule before you change anything in the repository.

## Running processes

Check for a running instance before you start a dev server, a build watcher, an emulator, or a database. Look at the
port, the process list, and the runner's output. Reuse what runs. Start a second instance only for a test that needs
isolation, or when the user asks in this conversation. A framework that moves to the next free port hides the duplicate:
two servers then serve different code. Stop what you started when the task ends.

## Thinking before coding

Read the relevant code before touching it. Understand the public interfaces, data flow, and how the modules work
together. Then think through your approach:

- Which change solves the problem correctly with the fewest steps?
- Which failures can occur? What happens with bad input, missing data, concurrent access, or network errors?
- Does this change affect other parts of the system? Trace the call chain.

Fix the cause of a failure. Do not hide it with a special case. Special cases include a longer time limit for one test,
a budget for one suite or system, an environment switch, and an option for one caller.

When you rename or move a file, update every reference: imports, documentation, configuration, and scripts.

Treat stored data and wire formats as contracts. Rename a stored key together with a migration of the stored data.
During a rolling deploy, readers accept both shapes until no old writer runs.

Before you add a module, folder, or helper, find the code that will call it. When you add a file, tell the user why that
code needs a new file.

## Scope discipline

- Complete the requested task. Do not expand scope.
- If you discover something unrelated that needs fixing, mention it to the user. Leave it unless the fix takes one small
  edit in a file you already change.
- Do not add features, refactor surrounding code, or make unrequested improvements.
- A request for a review or a plan stays read-only until the user allows changes.

## Verification and tests

Do not run verification broader than the change. Run no full test suite, build, scan, or Docker check unless the user
asks for it or the checks of the repository include it.

Write tests when the user asks or a check requires them. Fix each test that your change breaks. Language and framework
rules say how to write a test, not when.

## Rules and checks

Run `gspot explain <check>` to see what a check looks for and how to fix its findings. When a rule and a check conflict,
follow the check, and name both to the user.

## No defensive logic

Do not add guards, fallbacks, retries, defaults, or wrappers for states the public interface rules out. Handle known
failure modes where they can occur: user input, network calls, persistence, permissions, and external services. Trust an
internal invariant once the public interface establishes it. When an invariant lacks a clear promise, trace the code and
define the behavior instead of adding speculative protection.

## Abstractions

Keep one implementation of each concept, and one copy of each table of values, in the module that uses it. Extract
shared code only when two or more callers need the same behavior now.

- Delete each named function of `limits.trivial_function_statements` statements or fewer, two by default, exported or
  not, and inline its body at each call site. Methods, accessors, constructors, and recursive functions count too. A
  callback written inline has no name and stays.
- When a function of that size must stay, such as a method that an interface requires, ask the user. Then add a
  suppression comment with the reason.
- Keep a function with one caller when it names a step and holds more statements than that limit. Do not split code into
  functions only to pass a size or complexity limit. Split it by the steps it performs.
- An abstraction that gains flags, modes, or caller-specific branches needs a different design. Do not combine loosely
  related behaviors in a function behind a parameter that picks one.
- A function takes no positional boolean. Pass more than a few values as named fields: an options object, keyword-only
  parameters, or argument labels. `limits.function_parameters` sets the ceiling.
- To remove a wrong abstraction, inline it into each caller, delete the unused branches there, and extract only the
  common behavior that remains.
- Pass data, not a callback, unless it replaces several flags across real callers.
- Prefer plain functions, values, and explicit data flow to classes, factories, strategies, and inheritance. Push state
  and I/O outward, and keep the core close to pure.

## No backward compatibility

Never introduce compatibility layers, wrapper functions, re-exports for renamed symbols, deprecated-but-kept code, or
other backward-compatible scaffolding. A published API follows the deprecation policy its project declares instead.

When you replace or rename something:

- Delete the old implementation entirely.
- Update every call site to use the new version.

## Structure

Group constants, types, and schemas by the behavior they belong to.

# Python

Read this rule when you change Python code.

## Python scope

Importing a module does no I/O, starts no work, and parses no arguments.

## Runtime and files

Use the syntax of the declared Python version, stated once in the runtime pin. Name the version requirement of an
example whose syntax depends on it. Use `.py` for source and `.pyi` for stubs.

## Environment and settings

An importable module never depends on an active shell, a virtual environment, the current folder, or a globally
installed package. Imports resolve through project configuration, editable installs, `python -m`, or the configured
environment. Keep virtual environments and package caches out of commits.

The module that reads the settings takes the environment as a mapping, so a test passes its own:

```python
def parse_config(environ: Mapping[str, str]) -> AppConfig:
    """Parse the item limit that the environment sets.

    Args:
        environ: Environment values supplied by the application boundary.

    Returns:
        Settings containing a positive item limit.

    Raises:
        ValueError: MAX_ITEMS is missing, or is not an integer greater than zero.

    """
    max_items = int(environ.get('MAX_ITEMS', ''))
    if max_items < 1:
        message = 'MAX_ITEMS must be greater than zero'
        raise ValueError(message)
    return AppConfig(max_items=max_items)
```

## Module structure

Every runtime module has a docstring describing its present purpose.

## Imports

Imports resolve in the declared project environment, never through the script folder on `sys.path`. Break import cycles
by moving shared data or interfaces into a lower-level module.

### Import conventions

Take typing and `collections.abc` symbols directly. Use absolute cross-package imports. Explicit relative ones serve
siblings inside a package where surrounding code does that. Never use an implicit relative or dynamic import through
`importlib.import_module`, `__import__`, or `builtins.__import__`. In runtime code, never import inside a function,
method, or class body.

Direct symbol imports keep call sites readable. Import the module instead when its prefix identifies the source, as
`logging.getLogger(__name__)` does. Give every alias a reason. Valid reasons include a shared final name between two
modules, a collision with a local symbol, or too many words for the call site. A standard abbreviation such as `np` and
a disambiguated generic name also count.

## Docstrings

Write docstrings in the style that `tools.ruff.docstring_convention` names; Ruff and pydoclint both check it. Each
docstring matches its signature and behavior. The examples here use Google style.

A docstring that a library reads at run time, such as a pydantic model description or Click help, counts as product
text: changing it changes runtime output.

### Docstring conventions

- A class docstring says what an instance represents, never `Class that...`.
- A function that mutates an argument says so.

## Constants, globals, and mutable state

Prefer module constants. Do not expose mutable global state or lazy singletons as public API. Keep required mutable
state internal, and document its design reason. No ordinary call changes a module global as a hidden side effect.
Validated settings pass into the client or operation that consumes it, without a renaming wrapper.

### Constant naming

Name a private constant with one leading underscore, and retained module state for its concept.

## Main programs

An executable module puts its behavior in `main()`, runs it under the `__main__` guard, and prefers
`raise SystemExit(main())` when `main()` returns an exit code. Repository entry points run as
`python -m package.module`, and shell scripts call Python modules rather than inline snippets. A shebang appears only on
a file meant to execute directly.

## Functions

Do not hide I/O in a helper that looks like a pure transformation. Declare an ordinary no-result case in the signature
and return an explicit `None`. Input that violates the API contract raises a specific exception.

A generator expression serves a consumer that only needs a lazy projection. Comprehensions serve a single mapping or
filter. Write an ordinary loop for nested logic, several conditions, mutation, or a transformation that needs
explanation, so its order stays visible.

### Function conventions

A function owns one responsibility. Name it for its action and domain concept. Framework callbacks keep their required
names. Make side effects clear in its name or docstring.

A nested function closes over a local value to make the outer code clearer, and keeps its captured state and lifetime
explicit. It never exists to hide a helper from users or to turn a directly usable expression into a local call. A
module-level private helper serves reusable logic that a nested function hides. When a named helper only forwards a
conversion, put its body at the call site.

Write a lambda as a one-line expression at its consumer, such as a sorting key `lambda item: item.name`. Prefer a
generator expression or `operator` function over `map()` or `filter()` with a lambda. Use a `def` for anything longer. A
conditional expression holds one binary choice, `"stream" if is_streaming else "batch"`, and a path with several
operations gets `if` branches.

## Classes

Write a class only for real state, invariants, or behavior. Do not turn a coordinating function without polymorphism
into a class. Never group static functions into a class.

Keep classes that form one contract together, for example schemas, exceptions, protocols, and their records. Split
modules by independent responsibility, not by class count. Plain data has public attributes. Internal attributes carry
one leading underscore. Use a double underscore only to protect a base class from subclass collisions.

Keep `__init__` small: it takes the values the class needs rather than the external objects that carry them, and
validates invariants. Keep it separate from database rows, object-relational mapping (ORM) objects, API payloads, CLI
namespaces, or provider responses. An external representation enters through a classmethod named constructor such as
`from_row` or `from_payload` when the class owns that conversion. Neither `ClassName(**external_attributes)` nor a
constructor that only renames the initializer handles that conversion.

Keep loading, serialization, and validation systems outside the business object. Keep a derived attribute cheap and
deterministic. Build it from initialized fields; a named constructor handles derivation through I/O or complex parsing.

Use a dataclass as a typed plain record with methods only from its data contract. Mutable defaults use
`field(default_factory=...)`, and `__post_init__` holds cheap invariants and derived fields. Use a named constructor
when creation needs parsing, I/O, or alternate sources.

Never use it to disguise a mutable global configuration object. A frozen dataclass expresses a value fixed after
construction. A project on `attrs` applies the same principles through its factories, validators, and converters. Do not
add `attrs` in place of a small dataclass or a function.

```python
"""Represent an independently owned batch of prompt text."""

from dataclasses import field, dataclass

@dataclass
class Batch:
    """Prompt text owned by one processing batch.

    Attributes:
        prompts: The text items assigned to this batch.

    """

    prompts: list[str] = field(default_factory=list)

__all__ = ['Batch']
```

### Dataclass conventions

Document public dataclass fields in the configured docstring convention: `Attributes:` for Google style, an underlined
`Attributes` heading for NumPy.

A property provides cheap, unsurprising attribute access with no side effects. Never use it as a getter and setter over
an internal attribute, expensive work, a rename of a stored one, or a computation subclasses must override. Prefer
`@property` to a hand-written descriptor unless the public interface requires one.

## Inheritance and decorators

Design a class for inheritance or forbid it. Composition shares code, and protocols or small abstract base classes
define interfaces. Reserve specialization for a subclass that extends the base class and works wherever callers expect
its parent. Never mix code sharing, interface definition, and specialization in one hierarchy; keep it shallow, and keep
its classes together. Do not default to the template method pattern. A base class that defines control flow and calls
subclass hooks takes more work to read than a function with explicit delegation.

Do not put variants in one class with a type field and optional attributes that apply to some values. Make invalid
states unrepresentable. Behavior varying on more than one axis uses composition. Cross-cutting behavior such as
tracking, caching, timing, or logging uses a wrapper that records completion only after the operation succeeds. An
operation that varies by type without one class that handles it may use `functools.singledispatch`. A class meant for
subclassing documents its public and subclass APIs separately when the distinction matters.

A decorator removes real repetition or expresses a framework contract. It behaves unsurprisingly and preserves function
metadata. Because it runs at import time, it never depends on files, sockets, databases, or network calls. `classmethod`
marks named constructors and class-specific routines.

## Exceptions and error handling

Use explicit validation for external inputs and required preconditions. Avoid exceptions for ordinary branching when
code can check the value directly.

The following module accepts only bounded positive decimal integers and preserves the original conversion error.

Good:

```python
"""Validate limits supplied by a command or environment variable."""

MAX_BATCH_SIZE = 1000

def parse_batch_limit(raw: str) -> int:
    """Return a positive batch limit within the supported range."""
    try:
        value = int(raw)
    except ValueError as error:
        message = 'Batch limit must be a decimal integer.'
        raise ValueError(message) from error
    if not 1 <= value <= MAX_BATCH_SIZE:
        message = f'Batch limit must be between 1 and {MAX_BATCH_SIZE}.'
        raise ValueError(message)
    return value
```

## Exception contracts

A custom exception inherits from `Exception`, describes its condition in the docstring, and lives beside the behavior
that raises it rather than in a one-declaration file.

Do not substitute a built-in exception for the declared error type of an external API. Follow a library's public error
contract when callers depend on it.

## Assertions

Keep assertions in tests.

## Boolean logic and comparisons

Compare singleton values with `is None`, `is not None`, `is True`, or `is False` when the check concerns identity. Use
truth-value testing only when all falsy values mean the same thing. Do not treat an empty collection, zero, and a
missing value as interchangeable by default.

Use `==` for value equality. Use membership tests for supported containers, and avoid chained comparisons whose repeated
values have side effects. Keep evaluation order and short-circuit behavior intact when simplifying a condition.

### Control-flow conventions

Prefer direct predicates and early exits when they reduce nesting. Keep multi-step branches as statements.

## Iteration and collections

Iterate containers through their supported interfaces. Do not mutate a collection in a way that invalidates the current
iteration.

Read file objects as iterators instead of loading all lines when the operation can stream them. Use `yield from` to
delegate an iterator, and `any()` or `all()` for short-circuit predicate checks. Keep comprehensions limited to
transformations whose order and side effects remain clear.

Choose concrete return values or lazy iteration according to the caller's resource and reuse requirements, not solely to
shorten the implementation.

## Strings and output

Use f-strings for ordinary value interpolation. Preserve formatting that an external API requires. Keep logging
arguments apart from the message when the logger formats them lazily. Join a sequence of strings efficiently instead of
repeatedly growing one large value.

## Files and stateful resources

Use context managers for resources with an explicit lifetime. Close files and network resources on both success and
failure. Declare the encoding when opening a text file. Use binary mode for bytes instead of relying on an implicit
conversion.

A generator can keep a resource open while suspended. Make that lifetime clear to callers, especially when they can stop
consuming it early. This command reads the path supplied as its first argument and closes the input before printing the
collected records.

Good:

```python
"""Read normalized, nonempty records from a text file."""

import sys
from pathlib import Path

def main() -> int:
    """Read the first argument as a path and print its normalized records."""
    path = Path(sys.argv[1])
    with path.open(encoding='utf-8') as source:
        records = [record for line in source if (record := line.strip())]
    _ = sys.stdout.write('\n'.join(records))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
```

For large inputs, provide an explicit streaming interface whose caller owns the open resource or uses a context manager.
Do not materialize the full input only to avoid documenting its lifetime.

Write to a temporary file in the same folder, validate it, then rename it over the target. Clean up only paths and
resources owned by the current operation.

## Power features

Avoid power features unless the project already uses one and no plain alternative works. That covers custom metaclasses,
bytecode manipulation, dynamic inheritance, object reparenting, import hooks, runtime monkeypatching, and
reflection-heavy designs. It also covers interpreter internals, `__del__` cleanup, manual descriptors, and dynamic code
generation. Never use a power feature to shorten code or hide a dependency cycle. Ordinary functions, dataclasses, and
explicit imports and data structures come first.

## Threading

Built-in types and variable assignment do not synchronize threads. Use `queue.Queue` for communication and locks or
conditions for shared state, which stays small and explicit.

## Naming

### Python modules and imports

- Name test files `test_<behavior>.py`, grouped by behavior.
- Keep `__all__` names accurate and ordered according to local lint rules.

### Python types and dataclasses

- Give `Path` variables names that reveal whether they point to a folder, file, report, output, or repository root.
- Use `*_path` for filesystem paths and `*_dir` only for folders.
- Use `*_id` only for real identifiers. Never use it for arbitrary names or labels.
- Use `*_name` for display or provider names.
- Use `*_key` for dictionary and supported variant keys.

### Python boundary names

- Keep path construction with the code that owns the resource instead of repeating it in unrelated operations.

# Working on Python

These rules apply to Python source files, data modules, local linting tools,
runtime code, and CLI modules. They also apply to generated Python examples and
committed Python snippets.

Use this file together with [`GENERAL.md`](GENERAL.md), [`NAMING.md`](NAMING.md),
and the project's configured language and structural tooling.

Examples isolate the rule being explained. An abbreviated example does not
create an exception to the annotation, docstring, import, naming, or structure
rules in this guide.

## Contents

- [Core Python philosophy](#core-python-philosophy)
- [Source material decisions](#source-material-decisions)
- [Local tooling authority](#local-tooling-authority)
- [Runtime, encoding, and files](#runtime-encoding-and-files)
- [Environment and configuration](#environment-and-configuration)
- [Package installation security](#package-installation-security)
- [Module structure](#module-structure)
- [Imports](#imports)
- [Public and internal interfaces](#public-and-internal-interfaces)
- [Formatting](#formatting)
    - [Indentation](#indentation)
    - [Line length and wrapping](#line-length-and-wrapping)
    - [Blank lines](#blank-lines)
    - [Whitespace](#whitespace)
    - [Trailing commas](#trailing-commas)
    - [Parentheses](#parentheses)
    - [String quotes](#string-quotes)
- [Naming](#naming)
- [Comments and docstrings](#comments-and-docstrings)
    - [Comments](#comments)
    - [Docstrings](#docstrings)
    - [Module docstrings](#module-docstrings)
    - [Function and method docstrings](#function-and-method-docstrings)
    - [Class docstrings](#class-docstrings)
    - [Property docstrings](#property-docstrings)
    - [Override docstrings](#override-docstrings)
    - [TODO comments](#todo-comments)
- [Type annotations](#type-annotations)
    - [Annotation scope](#annotation-scope)
    - [Annotated metadata](#annotated-metadata)
    - [Using Any and object](#using-any-and-object)
    - [Input and return types](#input-and-return-types)
    - [Typing imports](#typing-imports)
    - [None and optional values](#none-and-optional-values)
    - [Generic types](#generic-types)
    - [Type aliases](#type-aliases)
    - [Type variables](#type-variables)
    - [Forward references](#forward-references)
    - [Protocols and interfaces](#protocols-and-interfaces)
    - [Variable annotations](#variable-annotations)
    - [Ignoring type errors](#ignoring-type-errors)
- [Constants, globals, and mutable state](#constants-globals-and-mutable-state)
- [Functions and methods](#functions-and-methods)
    - [Function size](#function-size)
    - [Default arguments](#default-arguments)
    - [Return statements](#return-statements)
    - [Nested functions and classes](#nested-functions-and-classes)
    - [Lambda functions](#lambda-functions)
    - [Conditional expressions](#conditional-expressions)
    - [Comprehensions and generator expressions](#comprehensions-and-generator-expressions)
    - [Generators](#generators)
- [Classes](#classes)
    - [Class design](#class-design)
    - [Initialization and named constructors](#initialization-and-named-constructors)
    - [Dataclasses](#dataclasses)
    - [Properties](#properties)
    - [Inheritance](#inheritance)
    - [Decorators](#decorators)
    - [Exceptions as classes](#exceptions-as-classes)
- [Exceptions and error handling](#exceptions-and-error-handling)
- [Assertions](#assertions)
- [Boolean logic and comparisons](#boolean-logic-and-comparisons)
- [Control flow simplification](#control-flow-simplification)
- [Iteration and collections](#iteration-and-collections)
- [Strings, logging, and error messages](#strings-logging-and-error-messages)
- [Files and stateful resources](#files-and-stateful-resources)
- [Main programs and top-level code](#main-programs-and-top-level-code)
- [Packages and Architecture](#packages-and-architecture)
    - [Package layout and import path](#package-layout-and-import-path)
- [Power features](#power-features)
- [Threading and concurrency](#threading-and-concurrency)
- [External integration boundaries](#external-integration-boundaries)
- [Manual verification](#manual-verification)
- [Verification commands](#verification-commands)
- [Review checklist](#review-checklist)
- [Anti-patterns](#anti-patterns)

## Core Python philosophy

Rules:

- Write readable Python before clever Python.
- Prefer explicit data flow, clear names, and small functions.
- Keep code import-stable. Importing a module must not touch external services,
  start background work, parse CLI arguments, or mutate runtime state.
- Prefer project-specific rules over generic style guides when they conflict.
- Prefer consistency with the surrounding module when a source guide allows more
  than one style.
- Do not make style-only churn outside the requested scope.
- Make public behavior clear through names, type annotations, and docstrings.
- Use exceptions for exceptional conditions, not for ordinary branch logic.
- Use built-in language features directly when they express the operation
  clearly.

Good Python is easy to scan:

```python
"""Yield request text from chat messages."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class PromptMessage:
    """One request message."""

    content: str


def iter_message_text(messages: Iterable[PromptMessage]) -> Iterable[str]:
    """Yield text content from request messages."""
    for message in messages:
        yield message.content


__all__ = [
    "PromptMessage",
    "iter_message_text",
]
```

Bad Python hides behavior and ownership:

```python
from examples import *

STATE = {"instance": None}


def get_instance():
    import importlib

    return importlib.import_module("loader").build_examples()
```

## Source material decisions

These rules adapt PEP 8, PEP 257, and the Google Python Style Guide into one
local standard for this repository.

| Topic                        | Local decision                                                                                                                                                                            |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Style authority              | Project rules and local tooling win over generic source guides.                                                                                                                           |
| Formatter line length        | Follow the line-length policy in the configured formatter.                                                                                                                                |
| Standard-library line length | PEP 8's standard-library limits do not define this repository's line length.                                                                                                              |
| Google line length           | Google's default does not override the configured line-length policy.                                                                                                                     |
| Formatter                    | Use the project's configured formatter. Do not hand-format against a different style.                                                                                                     |
| Linter                       | Use the configured linter, type checker, and structural checks. Map source-guide recommendations to those tools.                                                                          |
| Runtime                      | Use syntax supported by the project's declared minimum Python version.                                                                                                                    |
| Future imports               | Prefer `from __future__ import annotations` in Python modules.                                                                                                                            |
| Quotes                       | Use double quotes for ordinary strings unless another quote avoids escaping. Docstrings always use triple double quotes.                                                                  |
| Imports                      | Use explicit relative imports within a package. Use absolute imports for external packages and isolated worker entrypoints.                                                               |
| Class/function imports       | Direct imports of public classes, functions, and constants are allowed when they keep call sites readable. Import typing and `collections.abc` symbols directly.                          |
| `__all__`                    | Keep `__all__` at the bottom of modules. This local rule overrides PEP 8's normal module-dunder placement for `__all__`.                                                                  |
| Other module dunders         | Put dunders such as `__version__` after the module docstring and future imports, before ordinary imports.                                                                                 |
| License boilerplate          | Do not invent license boilerplate. Add it only if the project defines the exact boilerplate.                                                                                              |
| Function length              | Follow the configured function-size policy. Keep functions smaller when practical.                                                                                                        |
| File length                  | Follow the configured file-size policy.                                                                                                                                                   |
| Function typing              | Annotate function and method parameters and return values as required by this guide and the configured checks.                                                                            |
| Typing style                 | Within the supported runtime, use modern unions, built-in generics, explicit type aliases, Annotated for metadata, object for arbitrary objects, and protocols for structural interfaces. |
| Argument and return types    | Prefer abstract input types and concrete return types for concrete implementations. Avoid union return types that force caller-side type branching.                                       |
| Logging                      | Follow [GENERAL.md](GENERAL.md#logging). Do not create loggers, configure logging, or emit log records or stack traces.                                                                   |
| Project layout               | Respect the project's package structure; separate runtime code, declarative configuration, and development tooling. Do not patch `sys.path`.                                              |
| Inheritance                  | Prefer composition for code sharing, protocols for interfaces, and subclassing only for true specialization.                                                                              |
| Package installs             | Follow the shared host-environment policy below. Use the project lockfile for development and do not replace host-owned dependencies.                                                     |
| Verification                 | Follow [GENERAL.md](GENERAL.md#verification-scope).                                                                                                                                       |

When editing an existing file, follow the surrounding style where the source
guides allow a choice. When creating new code, use the decisions in this table.

## Local tooling authority

Use the project's configured formatter, linter, type checker, import-boundary
checks, and structural checks. Tools such as Ruff, BasedPyright, and
import-linter may implement these policies; their configuration belongs to the
project. [NAMING.md](NAMING.md) owns naming decisions.

Rules:

- Treat local lint failures as policy failures.
- Do not add per-file ignores, inline ignores, or broad config exceptions unless
  the user explicitly asks for a tooling change or the violation is unavoidable.
- Do not copy an existing per-file ignore into new files.
- Do not broaden an existing exception to make unrelated code pass.
- Do not disable a rule when a clear code change can satisfy it.
- Follow [verification scope](GENERAL.md#verification-scope) and use the
  configured commands for the requested scope.

Current local tooling constraints include:

- Python source under configured directories uses snake_case `.py` filenames.
- Follow the configured Python file-size policy.
- Follow the configured Python function-size policy.
- Runtime modules must not use local imports inside function, method, or class
  bodies.
- Runtime modules must not use lazy module loading, module-level lazy export
  hooks, or dynamic imports.
- Runtime modules must not use lazy singleton patterns.
- Runtime modules must not create import cycles.
- Apply [NAMING.md](NAMING.md#files-and-directories) for single-module
  packages, sibling filename prefixes, and configured structural exceptions.
- `__all__` must appear at the bottom of each module.
- Python logic must live in Python modules. Shell scripts must call it with
  `python -m`; do not embed inline Python in shell scripts.

## Runtime, encoding, and files

Rules:

- Use syntax supported by the project's declared minimum Python version.
  Examples using version-specific features apply only when that runtime is
  supported; do not raise the minimum version merely to copy an example.
  This runtime constraint also governs the modern typing syntax recommended
  throughout this guide. Use its supported equivalent when necessary.
- Store source files as UTF-8.
- Do not add an encoding declaration unless a tool or runtime requires it.
- Use LF line endings.
- Keep identifiers ASCII-only.
- Use English words for identifiers, comments, and docstrings unless an external
  identifier must keep another language or spelling.
- Use non-ASCII characters sparingly in string data.
- Do not use byte-order marks.
- Python filenames must use `.py`.
- Python filenames must be snake_case, except `__init__.py` and `__main__.py`.
- Python filenames must not contain dashes.
- Keep modules importable by pydoc, linting tools, and type checkers.

Bad:

```text
ModelConfig.py
model-config.py
model config.py
```

Good:

```text
model_config.py
modeling.py
__main__.py
```

## Environment and configuration

Rules:

- Treat environment variables as external text input.
- Read environment variables at a configuration or application boundary, not
  throughout business logic.
- Parse and validate environment-derived values once before passing them inward.
- Keep static configuration modules declarative. Do not put classes,
  dataclasses, function calls, or comprehensions there. Put typed runtime
  representations and derived indexes with their runtime owner.
- Store secrets in environment variables or a secret manager, never in source
  code, documentation examples, or checked-in configuration.
- Do not use a real-looking default for a secret. Fail at startup or command
  initialization when a required secret is missing.
- Do not make importable modules depend on an active shell, virtual
  environment, current working directory, or globally installed package.
- Use project configuration, editable installs, `python -m`, or the configured
  environment to resolve imports.
- Do not commit virtual environment directories or generated package caches.

Good runtime representation:

```python
@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from the environment."""

    max_items: int


def read_config(environ: Mapping[str, str]) -> AppConfig:
    """Read runtime configuration from environment variables."""
    raw_max_items = environ.get("MAX_ITEMS", str(DEFAULT_MAX_ITEMS))
    return AppConfig(max_items=int(raw_max_items))
```

Bad:

```python
def list_items() -> list[Item]:
    limit = int(os.getenv("MAX_ITEMS", "100"))
    return query_items(limit=limit)
```

## Package installation security

When a package runs inside another application's shared Python environment,
use the host's interpreter for installation and respect host-owned dependencies.
Keep compatible runtime constraints in the authoritative package metadata.
Generate any secondary dependency manifests from that source. Use the project's
configured environment for standalone applications.

Rules:

- Use the project's committed lockfile for the development environment.
- Install dependencies through the existing project task when installation is
  requested. Run dependency checks only when explicitly requested.
- Review dependency and lock changes. Do not bypass a resolver conflict or copy
  vulnerability exceptions from another project.
- Prefer compatible wheels. Review any required source build and its tools.
- Use a single trusted package index. Do not add `--extra-index-url` for private
  packages; use a controlled index or reviewed local wheels.
- Use `--no-deps` only after resolving and installing the selected environment's
  required packages.
- Install the local project through the package installer. Do not use
  `python setup.py install`, `python setup.py develop`, or `easy_install`.
- Do not change host dependencies merely to satisfy development tooling.
- When a dependency audit is requested, check the resolved dependency versions.

When distribution verification is requested, build and install the actual
package in the local host. An editable development import does not prove that
the distributed package works.

## Module structure

Order module contents this way:

1. Module docstring.
1. `from __future__ import annotations`, when used.
1. Other module dunders, except `__all__`.
1. Imports.
1. Module constants.
1. Type aliases.
1. Dataclasses and classes.
1. Functions.
1. `if __name__ == "__main__":` guard, when the module is executable.
1. `__all__` at the bottom.

Rules:

- Give every Python module a docstring that describes its present purpose.
- Keep top-level code limited to declarations, constants, imports, and cheap
  initialization.
- Do not perform I/O, network calls, CLI parsing, or long computations at import
  time.
- Do not mutate global runtime state at import time except for declared
  constants and deliberate local configuration.
- Keep `__all__` explicit for modules with a public API.
- Use `__all__ = []` when a module intentionally exports no public names.

## Imports

Rules:

- Put imports at the top of the file, after the module docstring and future
  imports.
- Keep ordinary imports in one flat block. Do not separate standard-library,
  third-party, first-party, or sibling imports with blank lines.
- Put one-line imports before multiline or explicitly parenthesized imports.
- Sort one-line imports by the total rendered statement length. Break equal
  lengths by case-insensitive statement text and then exact statement text.
- Sort multiline or explicitly parenthesized imports by the rendered import
  header length using the same text tie-breakers.
- Sort names inside grouped imports by rendered name length using the same text
  tie-breakers.
- Apply the same ordering and spacing rules inside a top-level bare
  `if TYPE_CHECKING:` body.
- Put a blank line after each completed import block.
- Use one import per line for ordinary imports.
- Import typing and `collections.abc` symbols directly.
- Use explicit relative imports within a package, consistent with the
  supported entrypoint loading contract.
- Use absolute imports for external packages and isolated worker entrypoints.
- Never use implicit relative imports.
- Never use wildcard imports.
- Never import inside function, method, or class bodies in runtime code.
- Never use dynamic imports through `importlib.import_module`, `__import__`, or
  `builtins.__import__` in runtime code.
- Do not rely on the main script directory being present on `sys.path`.
- Avoid circular imports by moving shared data or contracts into a lower-level
  owner.

Good:

```python
from __future__ import annotations

import io
import numpy as np
from PIL import Image
from pathlib import Path
from ..config.paths import PRESETS_DIRECTORY
from ..errors import ErrorCode, RequestError
from collections.abc import Iterable, Sequence
```

Bad:

```python
import os, sys
from examples import *


def build():
    import src.media.state
```

Direct symbol imports are acceptable for public classes, functions, constants,
and typing symbols when they make the call site clearer:

```python
from pathlib import Path
from typing import Literal
from dataclasses import dataclass
from ..errors import ErrorCode, RequestError
```

Use module imports when the module prefix makes ownership clearer:

```python
import random

rng = random.Random(seed)
```

Do not import a module only to hide a vague name:

```python
from storage.file_system import options as fs_options
```

Follow [NAMING.md](NAMING.md#python-modules-and-imports) for alias permissions.
Length or a vague exported name alone does not justify an alias; improve names
you own instead of hiding them behind another name.

## Public and internal interfaces

Rules:

- Public names are names intended for callers outside the module.
- Internal names use one leading underscore.
- Do not use double-leading underscores unless avoiding subclass collisions in a
  class designed for inheritance.
- Do not invent double-leading and double-trailing dunder names.
- Use `__all__` to declare public module exports.
- Imported names are implementation details unless explicitly exported through
  `__all__`.
- Do not rely on indirect access to names imported by another module.
- Public attributes do not have leading underscores.
- Internal modules, functions, constants, and attributes have one leading
  underscore.

Bad:

```python
def __normalize_label__(value):
    return int(value)
```

## Formatting

Use Ruff format as the source of truth for mechanical formatting.

Rules:

- Do not fight the formatter.
- Do not hand-align code in ways the formatter will undo.
- Do not use semicolons.
- Do not put multiple statements on one line.
- Keep formatting consistent with the surrounding file when the formatter allows
  more than one readable option.

### Indentation

Rules:

- Use 4 spaces per indentation level.
- Never use tabs.
- Use implicit continuation inside parentheses, brackets, and braces.
- Prefer hanging indents with one argument or item per line when a call or
  literal is too long.
- When using a hanging indent, put no arguments on the first line.
- Align closing delimiters with the construct start when the values are split
  across lines.

Good:

```python
result = long_function_name(
    first_argument,
    second_argument,
    third_argument,
)
```

Good:

```python
result = long_function_name(first_argument, second_argument, third_argument)
```

Bad:

```python
result = long_function_name(first_argument, second_argument, third_argument)
```

Long conditionals may use extra indentation to distinguish the condition from
the body:

```python
if config is None or "editor.language" not in config or config["editor.language"].use_spaces is False:
    use_tabs()
```

### Line length and wrapping

Rules:

- Follow the line-length limit in the local Ruff configuration.
- Prefer shorter lines when they are naturally readable.
- Keep docstring summary lines concise and on one physical line.
- Wrap long expressions with implicit continuation inside parentheses, brackets,
  and braces.
- Do not use backslashes for line continuation.
- Break before binary operators in new multiline arithmetic or boolean
  expressions when that improves readability.
- Prefer breaking at the highest syntactic level.
- Do not split a name from its type annotation unless the name and type together
  cannot fit readably.
- Put long URLs on their own comment line instead of splitting them.

Good:

```python
income = gross_wages + taxable_interest + (dividends - qualified_dividends) - ira_deduction - student_loan_interest
```

Bad:

```python
income = gross_wages + taxable_interest + (dividends - qualified_dividends) - ira_deduction - student_loan_interest
```

Good:

```python
message = "This long string is split through implicit literal concatenation inside parentheses."
```

Bad:

```python
message = "This long string is split with an explicit continuation character."
```

### Blank lines

Rules:

- Use two blank lines between top-level function and class definitions.
- Use one blank line between methods inside a class.
- Use one blank line between a class docstring and the first method.
- Use blank lines inside functions sparingly to separate logical sections.
- Do not add blank lines immediately after a `def` line.
- Do not use large blank-line blocks as visual decoration.

Good:

```python
def build_examples() -> list[PromptExample]:
    """Build examples."""
    return []


def count_examples(examples: list[PromptExample]) -> int:
    """Return the number of examples."""
    return len(examples)
```

Bad:

```python
def build_examples() -> list[PromptExample]:

    return []
```

### Whitespace

Rules:

- Do not use extra whitespace inside parentheses, brackets, or braces.
- Do not use whitespace before commas, semicolons, or colons.
- Use one space after commas and colons, except at the end of a line.
- Do not use whitespace before the opening parenthesis of a function call.
- Do not use whitespace before indexing or slicing brackets.
- Surround assignment, augmented assignment, comparisons, identity checks,
  membership checks, and boolean operators with one space on each side.
- Use judgment around arithmetic operators, but never use more than one space on
  either side.
- Do not vertically align assignments, comments, dictionary colons, or other
  tokens with extra spaces.
- Do not leave trailing whitespace.

Good:

```python
spam(ham[1], {"eggs": 2})
x = 1
long_name = 2
if value is not None:
    return value
```

Bad:

```python
spam(ham[1], {"eggs": 2})
x = 1
long_name = 2
if value == None:
    return value
```

For slices, treat the colon like a low-priority binary operator when both sides
are complex. Omit spaces when an endpoint is omitted.

Good:

```python
items[1:9]
items[:9]
items[lower + offset : upper + offset]
items[: upper_fn(x) : step_fn(x)]
```

Bad:

```python
items[1:9]
items[lower + offset : upper + offset]
items[:upper]
```

### Trailing commas

Rules:

- Use a trailing comma in multiline literals, argument lists, imports, and
  `__all__`.
- Do not use a redundant trailing comma when the closing delimiter is on the
  same line.
- Use a trailing comma for a one-item tuple, preferably inside parentheses.

### Parentheses

Rules:

- Use parentheses for grouping, tuples, and implicit line continuation.
- Do not wrap simple conditions in unnecessary parentheses.
- Do not wrap simple return values in unnecessary parentheses.
- Parenthesize one-item tuples for clarity.
- Returning a tuple may use parentheses when it improves readability.

Good:

```python
if is_ready:
    return value

singleton = (value,)
return first, second
```

Bad:

```python
if is_ready:
    return value
```

### String quotes

Rules:

- Use double quotes for ordinary strings in new code.
- Use single quotes only when it avoids escaping or matches surrounding code the
  formatter preserves.
- Use triple double quotes for docstrings.
- Prefer triple double quotes for multiline strings.
- Do not create string literals with significant trailing whitespace.
- Use `textwrap.dedent()` when a multiline string must not include indentation.

Good:

```python
name = "example"
message = "It's ready."
doc = """One multiline string."""
```

Bad:

```python
name = "example"
doc = """A docstring-like string."""
```

## Naming

Follow [`NAMING.md`](NAMING.md) for all naming choices.

The [Python naming rules](NAMING.md#python) cover case, exception and type
names, private names, conventional method parameters, and keyword collisions.
The examples below illustrate those rules.

Good:

```python
class RuntimeConfig:
    """Runtime configuration."""


def build_examples(source_items: list[object]) -> list[PromptExample]:
    """Build examples from raw items."""
    ...


MAX_EXAMPLES = 1000
class_: str
```

Bad:

```python
class runtime_config: ...


def buildExamples(data): ...


maxExamples = 1000
clss = "value"
```

## Comments and docstrings

Comments and docstrings must match [`GENERAL.md`](GENERAL.md).

Rules:

- Describe present behavior only.
- Do not include change history.
- Do not mention removed, replaced, renamed, or previous code.
- Do not reference specific file paths unless the reference is essential and
  stable.
- Keep comments and docstrings accurate when behavior changes.
- Use clear English.
- Use complete sentences for block comments and docstrings.
- Keep punctuation, spelling, and grammar clean.

### Comments

Rules:

- Use comments to explain intent, invariants, edge cases, and non-obvious
  choices.
- Do not narrate obvious code.
- Block comments apply to the code that follows and use `#` plus one space on each line.
- Inline comments are separated from code by at least two spaces and start with
  `#` plus one space.
- Use inline comments sparingly.
- Keep comments up to date when code changes.

Good:

```python
# A file handle prevents an input string from being interpreted as a URL.
with source_path.open("rb") as source_file:
    read_source(source_file)
```

Bad:

```python
records = read_records()  # Read records
```

When suppressing a linter warning, keep the suppression narrow and give the
specific reason:

```python
try:
    result = read_worker_result()
except Exception:  # noqa: BLE001 -- reason: The process boundary returns a fixed failure result.
    result = WorkerResult.failed()
```

Do not add broad suppressions:

```python
# noqa
```

### Docstrings

Rules:

- Use triple double quotes for all docstrings.
- Write docstrings for every module, function, class, and method covered by the
  local documentation checks, including private and nested declarations.
- One-line docstrings stay on one line and end with punctuation.
- Multiline docstrings start with a one-line summary, then a blank line, then
  details.
- Put the closing triple quotes of a multiline docstring on their own line.
- Do not restate the signature in a docstring.
- Document arguments, return values, yielded values, side effects, and raised
  exceptions when they are part of the interface.
- Do not document exceptions raised only when callers violate the documented
  contract.
- Keep docstring style consistent within a file. Descriptive style and
  imperative style are both allowed by the source material.

Good one-line docstring:

```python
def build_token_budget(prompt_tokens: int, output_tokens: int) -> int:
    """Return the total token budget."""
    return prompt_tokens + output_tokens
```

Bad one-line docstring:

```python
def build_token_budget(prompt_tokens: int, output_tokens: int) -> int:
    """build_token_budget(prompt_tokens, output_tokens) -> int"""
    return prompt_tokens + output_tokens
```

Good multiline docstring:

```python
def read_rows(keys: Sequence[str]) -> Mapping[str, tuple[str, ...]]:
    """Read rows for the requested keys.

    Retrieves one row for each key that exists in the backing table.

    Args:
        keys: Keys to fetch.

    Returns:
        A mapping from key to row values.

    Raises:
        OSError: The backing table could not be read.
    """
```

### Module docstrings

Rules:

- Start every Python module with a docstring that describes the module's
  purpose.
- A module docstring may include a short usage example when it helps callers.

### Function and method docstrings

Rules:

- Apply the configured documentation coverage described under
  [docstrings](#docstrings) and the
  [required-comment standard](GENERAL.md#required-comments).
- Functions that mutate an argument must say so.
- Generator functions use `Yields:` instead of `Returns:`.
- `Returns:` may be omitted when the one-line summary already fully describes
  the returned value.
- Do not document `None` returns unless it clarifies control flow.
- Use `Args:`, `Returns:`, `Yields:`, and `Raises:` sections when needed.
- Keep section indentation consistent within a file.

Bad:

```python
def build_engine_settings(engine, path, tokens):
    """build_engine_settings(engine, path, tokens)."""
```

### Class docstrings

Rules:

- Apply the configured documentation coverage described under
  [docstrings](#docstrings).
- A class docstring starts with a one-line summary describing what an instance
  represents.
- Public attributes, excluding properties, are documented in an `Attributes:`
  section.
- Exception class docstrings describe the condition represented by the
  exception, not the raising site.
- Do not write "Class that..." as the summary.

Good:

```python
@dataclass
class RuntimePrompt:
    """Single runtime prompt example.

    Attributes:
        prompt: Normalized prompt text.
        expected_status: Expected response status.
        group: Group identifier for related prompts.
    """

    prompt: str
    expected_status: str
    group: str
```

Bad:

```python
class RuntimePrompt:
    """Class that stores a runtime prompt."""
```

### Property docstrings

Rules:

- Property docstrings describe the attribute, not the method action.
- Use attribute-style wording.
- Do not write "Returns..." for a property unless the surrounding file already
  uses that style.

Good:

```python
@property
def num_labels(self) -> int:
    """The number of supported runtime labels."""
    return len(self.labels)
```

Bad:

```python
@property
def num_labels(self) -> int:
    """Returns the number of supported runtime labels."""
    return len(self.labels)
```

### Override docstrings

Rules:

- Overridden methods require docstrings. Describe any behavior, side effects,
  constraints, or return semantics that differ from the base contract.
- Use `typing.override`.

Good:

```python
from typing import override


class Child(Parent):
    """Child implementation of the parent contract."""

    @override
    def build(self) -> Result:
        """Build the result defined by the parent contract."""
        return super().build()
```

### TODO comments

Rules:

- Use TODO comments only for temporary, tracked work.
- A TODO starts with `TODO:`, then a link or issue reference, then `-`, then an
  explanation.
- Do not use individual names or team names as TODO ownership.
- Do not add TODOs for vague future improvements.
- Include a specific event or date when the TODO depends on time or an external
  milestone.

Good:

```python
# TODO: https://example.com/issues/123 - Remove this branch when all exports use JSONL.
```

Bad:

```python
# TODO: clean this up later
# TODO(alex): fix this
```

## Type annotations

Type annotations improve readability and catch type-related errors. They are
especially important for public APIs, stable code, complex data shapes, and
model or data boundaries.

### Annotation scope

Rules:

- Annotate every function and method parameter and return value required by the
  local Ruff configuration.
- Annotate data structures crossing module boundaries.
- Annotate code that is prone to type-related errors.
- Annotate code when it becomes stable from a type perspective.
- Do not annotate `self` or `cls` unless needed for precise typing.
- Annotate `__init__` as returning `None`.
- Use `Any` only when the type is genuinely unconstrained or cannot be
  expressed clearly.
- Do not add obsolete `# type:` comments.
- Where the supported runtime permits it, prefer modern shorthand over
  `typing.Union`, `typing.Optional`, `typing.List`, `typing.Dict`, and
  `typing.Type` aliases.

Private helpers follow the same annotation rule:

```python
def _token_count(value: int) -> int:
    return int(value)
```

### Annotated metadata

Rules:

- Use `typing.Annotated` when a framework or validation library needs metadata
  attached to a normal Python type.
- Put the real type first. Put framework or validation metadata after it.
- Keep defaults as ordinary Python parameter defaults when using
  `Annotated`.
- Do not put conflicting defaults in both the metadata object and the function
  signature.
- Do not use arbitrary string metadata as a substitute for clear domain types,
  validators, or documented framework metadata.
- Prefer `Annotated` over older framework styles that replace the Python
  default value with a metadata object.

Good:

```python
def read_items(query: Annotated[str | None, Query(max_length=MAX_QUERY_LENGTH)] = None) -> list[Item]:
    return find_items(query=query)
```

Bad:

```python
def read_items(query: str | None = Query(default=None, max_length=50)) -> list[Item]:
    return find_items(query=query)
```

Bad conflicting defaults:

```python
def read_items(query: Annotated[str, Query(default="recent")] = "popular") -> list[Item]:
    return find_items(query=query)
```

### Using Any and object

Rules:

- Use `object` when a value can be any Python object and the function uses only
  operations available on all objects. Passing the value to `str()` is one
  example.
- Use `object` for callback return values when the callback return value is
  ignored.
- Use `Any` when the type cannot be expressed accurately, the correct type would
  make the API unreasonably hard to use, or the value intentionally escapes type
  checking.
- Do not use `Any` to avoid writing a precise type.
- Prefer a protocol, type variable, overload, or small value object over `Any`
  when that models the contract clearly.

Good:

```python
def format_for_display(value: object) -> str:
    """Format any object for display."""
    if isinstance(value, int):
        return f"{value:02}"
    return str(value)


def call_callback(callback: Callable[[int], object]) -> None:
    """Call a callback and ignore its return value."""
    callback(42)
```

Bad:

```python
def format_for_display(value: Any) -> str:
    return str(value)


def call_callback(callback: Callable[[int], None]) -> None:
    callback(42)
```

### Input and return types

Rules:

- For arguments, prefer protocols and abstract collection types such as
  `Iterable`, `Sequence`, `Mapping`, and `Callable`.
- For arguments that accept any value, use `object`, not `Any`.
- For concrete implementations, return concrete types such as `list`, `dict`,
  and concrete dataclasses.
- For protocols and abstract base classes, choose return types case by case
  based on the promised interface.
- Avoid union return types when callers must immediately branch with
  `isinstance()` to use the result.
- If different result shapes require different caller behavior, prefer separate
  functions, a tagged dataclass, a protocol, or a small hierarchy with a clear
  common contract.
- Use `float` instead of `int | float` for numeric APIs where integers are valid
  float inputs.
- Use `None`, not `Literal[None]`.

Good:

```python
def map_lengths(values: Iterable[str]) -> list[int]:
    return [len(value) for value in values]


def create_label_map() -> dict[str, int]:
    return {"reject": 0, "accept": 1}


def to_display_text(value: object) -> str:
    return str(value)
```

Bad:

```python
def map_lengths(values: list[str]) -> list[int]:
    return [len(value) for value in values]


def create_label_map() -> MutableMapping[str, int]:
    return {"reject": 0, "accept": 1}


def to_display_text(value: Any) -> str:
    return str(value)
```

### Typing imports

Rules:

- Import symbols from `typing` and `collections.abc` directly.
- Prefer `collections.abc` abstract containers for input types.
- Prefer built-in generic types such as `list[str]`, `dict[str, int]`, and
  `tuple[str, ...]`.
- Do not use `typing.List`, `typing.Dict`, or `typing.Tuple` in new code when
  the supported runtime permits built-in generic types.
- Do not use `typing.Type`; use built-in `type`.
- Do not use `typing.Union` or `typing.Optional`; use `|`.
- Do not use `typing.Text` in new code.
- Use `str` for text and `bytes` for binary data.
- Use `AnyStr` only when multiple string annotations must all be the same text
  or binary type.

Good:

```python
from typing import Any, Literal
from collections.abc import Mapping, Iterable, Sequence


def transform(rows: Sequence[tuple[str, int]]) -> Mapping[str, int]: ...
```

Bad:

```python
from typing import Dict, List, Type, Tuple


def transform(rows: List[Tuple[str, int]]) -> Dict[str, int]: ...


def build(cls: Type[ModelConfig]) -> ModelConfig: ...
```

### None and optional values

Rules:

- Use explicit `X | None` for nullable values.
- Put `None` last in union annotations.
- Do not rely on implicit optional inference from a default of `None`.
- Use `is None` and `is not None` for None checks.
- When a parameter is nullable and has a default, annotate it as nullable.

Good:

```python
def read_examples(path: Path | None = None) -> list[PromptExample]:
    if path is None:
        path = DEFAULT_INPUT_PATH
    ...
```

Bad:

```python
def normalize(value: None | str) -> str: ...


def read_examples(path: Path = None) -> list[PromptExample]:
    path = path or DEFAULT_INPUT_PATH
```

### Generic types

Rules:

- Specify type parameters for generic types.
- Do not write bare `Sequence`, `Mapping`, `list`, or `dict` unless the element
  type is intentionally unconstrained and made explicit with `Any`.
- Prefer `TypeVar` when a relationship between input and output types matters.

Good:

```python
def get_names(employee_ids: Sequence[int]) -> Mapping[int, str]: ...
```

Bad:

```python
def get_names(employee_ids: Sequence) -> Mapping: ...
```

Good when preserving the key type:

```python
_T = TypeVar("_T")


def get_names(employee_ids: Sequence[_T]) -> Mapping[_T, str]: ...
```

### Type aliases

Rules:

- Use type aliases for complex repeated types.
- Follow [NAMING.md](NAMING.md#python-case-rules) for type alias names.
- Use `type` statements for aliases when the declared minimum runtime supports
  them. Otherwise use explicit alias syntax supported by that runtime.
- Do not use `TypeAlias` for ordinary value, module, class, function, constant,
  or path aliases.

Good:

```python
type _LossGradient = tuple[torch.Tensor, torch.Tensor]
type MetricMap = Mapping[str, float]
```

Bad:

```python
_LossGradient = tuple[torch.Tensor, torch.Tensor]
Path: TypeAlias = pathlib.Path
ERROR_EXISTS: TypeAlias = errno.EEXIST
```

### Type variables

Rules:

- Private unconstrained type variables may use `_T`, `_P`, and similar short
  names.
- Public or constrained type variables must have descriptive names.
- Use `_co` and `_contra` suffixes for covariant and contravariant variables.
- Do not use public single-letter `T` or `P` for type variables.

Good:

```python
from collections.abc import Callable
from typing import TypeVar, ParamSpec

_P = ParamSpec("_P")
_T = TypeVar("_T")
AddableType = TypeVar("AddableType", int, float, str)
AnyFunction = TypeVar("AnyFunction", bound=Callable)
```

Bad:

```python
T = TypeVar("T")
_F = TypeVar("_F", bound=Callable)
_T = TypeVar("_T", int, float, str)
```

### Forward references

Rules:

- Prefer `from __future__ import annotations` for forward references.
- Do not remove `from __future__ import annotations` only because newer Python
  versions defer annotation evaluation. Check the supported runtime versions
  and runtime annotation consumers before changing this convention.
- Use string annotations only when future annotations are not available or when
  needed for a type-checking-only import pattern.
- Avoid type-only circular imports. They are design pressure to move shared
  contracts.

Good:

```python
from __future__ import annotations


class Node:
    def __init__(self, parent: Node | None = None) -> None:
        self.parent = parent
```

Acceptable when avoiding a runtime import strictly for typing:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from external_package import ExternalType


def build(value: "ExternalType") -> str: ...
```

### Protocols and interfaces

Rules:

- Prefer `typing.Protocol` for structural interfaces used by a consumer.
- Keep protocols narrow. Define only the attributes and methods the consumer
  needs.
- Place a protocol near the consumer when it describes what that consumer needs,
  not what an implementation happens to provide.
- Use `@runtime_checkable` only when runtime `isinstance()` checks are truly
  needed.
- Use abstract base classes when nominal identity, runtime instantiation checks,
  or a standard-library ABC contract is the real requirement.
- Do not use an abstract base class to share implementation code.
- Do not mix interface definition with subclass-based code sharing.
- Implementations do not need to import or subclass a protocol for type checkers
  to recognize that they satisfy it.

Good:

```python
class Reader(Protocol):
    def read(self) -> str: ...


def print_reader(reader: Reader) -> None:
    print(reader.read())
```

Good implementation:

```python
class FileReader:
    def read(self) -> str:
        return "contents"
```

Bad:

```python
class BaseReader(abc.ABC):
    def read_and_print(self) -> None:
        print(self.read())

    @abc.abstractmethod
    def read(self) -> str: ...
```

### Variable annotations

Rules:

- Use variable annotations when the inferred type is unclear or impossible.
- Use one space after the colon.
- Do not use a space before the colon.
- If assigning a value, use one space around `=`.

Good:

```python
examples: list[PromptExample] = []
label_by_name: dict[str, int] = {}
```

Bad:

```python
examples: list[PromptExample] = []
label_by_name: dict[str, int] = {}
```

### Ignoring type errors

Rules:

- Avoid `# type: ignore`.
- If an ignore is necessary, keep it line-scoped.
- Include the specific error code when the type checker supports it.
- Do not keep unused ignores.
- Prefer refactoring or a clearer annotation over suppressing a type error.

Good:

```python
value = untyped_api()  # pyright: ignore[reportUnknownVariableType] -- reason: The package has no type data.
```

Bad:

```python
# type: ignore
```

## Constants, globals, and mutable state

Rules:

- Module constants are allowed and encouraged when the module owns the value.
- Put static defaults, limits, patterns, and configurable values in the
  declarative configuration owner.
- Follow [NAMING.md](NAMING.md#python) for constant names and visibility.
- Avoid mutable global state.
- Do not use lazy singleton state.
- Do not create module-level `STATE`, `_STATE`, `INSTANCE`, `_INSTANCE`, or
  `_instance` holders.
- Do not expose mutable globals directly as public API.
- If mutable global state is genuinely required, keep it internal and document
  the design reason.
- Do not mutate module globals as a hidden side effect of ordinary function
  calls.

Good in a declarative configuration module:

```python
DEFAULT_TIMEOUT_SECONDS = 30
MAX_RETRY_ATTEMPTS = 3
```

Bad:

```python
STATE = {"instance": None}
_INSTANCE = None
```

Prefer passing state explicitly:

```python
def build_client(config: ClientConfig) -> Client:
    return Client(config)
```

Do not hide process-wide state behind lifecycle helpers:

```python
def get_instance() -> Client: ...
```

## Functions and methods

Rules:

- Keep functions focused on one responsibility.
- Prefer plain functions and explicit data flow before classes.
- Name functions by action and domain concept.
- Do not use `process`, `handle`, `run`, `execute`, or `do_work` when a more
  precise action exists.
- Use `handle` only for callbacks, framework boundaries, event handlers, or
  signal handlers.
- Keep side effects explicit in the name or docstring.
- Do not hide I/O in helpers that look like pure transformations.

### Function size

Rules:

- Keep functions small and focused.
- Follow the configured function-size limit.
- If a function approaches the limit, consider extracting real sub-operations.
- Do not split a function into meaningless helpers only to satisfy the count.
- Extract helpers when the extracted operation has a clear name and contract.

Good extraction:

```python
def _trim_history_messages(
    messages: Sequence[HistoryMessage],
    max_messages: int,
) -> list[HistoryMessage]:
    if len(messages) <= max_messages:
        return list(messages)
    return list(messages[-max_messages:])
```

Bad extraction:

```python
def _part_one(data): ...


def _part_two(data): ...
```

### Default arguments

Rules:

- Do not use mutable objects as default argument values.
- Use `None` as the default and create the mutable value inside the function.
- Immutable defaults such as `None`, strings, numbers, booleans, and tuples are
  allowed.
- Do not use dynamic values such as `time.time()` as defaults.
- Do not use parsed flag values, environment-dependent values, or mutable global
  values as defaults.
- When an annotated parameter has a default, put spaces around `=`.
- When an unannotated parameter has a default, do not put spaces around `=`.

Good:

```python
def collect_labels(labels: Sequence[str] | None = None) -> list[str]:
    if labels is None:
        labels = []
    return list(labels)
```

Bad:

```python
def collect_labels(labels: list[str] = []) -> list[str]:
    return labels
```

Good formatting:

```python
def resize(width: int = 0, height: int = 0) -> None: ...
```

Bad formatting:

```python
def resize(width: int = 0, height: int = 0) -> None: ...
```

### Return statements

Rules:

- Be consistent in return statements.
- If any return statement returns a value, explicitly return `None` from every
  no-value path or end with a clear final return.
- Do not mix `return` and `return value` in the same function.
- Do not rely on implicit `None` when an explicit no-result path is meaningful.

Good:

```python
def safe_sqrt(value: float) -> float | None:
    if value < 0:
        return None
    return math.sqrt(value)
```

Bad:

```python
def safe_sqrt(value: float) -> float | None:
    if value >= 0:
        return math.sqrt(value)
```

### Nested functions and classes

Rules:

- Nested functions are allowed when they close over a local value and make the
  outer function clearer.
- Nested classes are allowed for narrowly scoped helper types.
- Do not nest a function only to hide it from users.
- Prefer a module-level private helper when real callers need direct access.
- Avoid nested functions that make the outer function long or hard to scan.

Good:

```python
def build_adder(summand: float) -> Callable[[float], float]:
    """Return a function that adds a fixed summand."""

    def add(value: float) -> float:
        return summand + value

    return add
```

Bad:

```python
def build_examples(data: list[object]) -> list[PromptExample]:
    def normalize_prompt(value: object) -> str:
        return str(value).strip()

    ...
```

Use a module helper instead:

```python
def _normalize_prompt(value: object) -> str:
    return str(value).strip()
```

### Lambda functions

Rules:

- Lambdas are allowed for simple one-line expressions.
- Do not bind a lambda directly to a name. Use `def`.
- Prefer generator expressions over `map()` or `filter()` with a lambda.
- Use functions from `operator` for common operations when they are clearer.
- If a lambda spans multiple lines or becomes hard to read, use a named
  function.

Good:

```python
def double(value: int) -> int:
    return value * 2


sorted_items = sorted(items, key=lambda item: item.name)
```

Bad:

```python
double = lambda value: value * 2
```

### Conditional expressions

Rules:

- Conditional expressions are allowed for simple cases.
- Keep each part easy to read: true expression, condition, false expression.
- Use a full `if` statement when the expression becomes long or nested.

Good:

```python
mode = "stream" if is_streaming else "batch"
```

Bad:

```python
mode = (
    choose_streaming_mode(request, config)
    if complicated_condition(request, config, metadata)
    else choose_batch_mode(request, config, metadata)
)
```

### Comprehensions and generator expressions

Rules:

- Use comprehensions for simple mapping or filtering.
- Do not use multiple `for` clauses or multiple filter expressions in one
  comprehension.
- Optimize for readability, not compactness.
- Use ordinary loops for nested logic, multiple conditions, mutation, or
  non-obvious transformations.
- Generator expressions are preferred when a list is not needed.

Good:

```python
names = [user.name for user in users if user is not None]
```

Good with a long expression:

```python
valid_examples = [transform_example(example) for example in examples if is_valid_example(example)]
```

Bad:

```python
pairs = [(x, y) for x in range(10) for y in range(5) if x * y > 10]
```

Use a loop:

```python
pairs: list[tuple[int, int]] = []
for x in range(10):
    for y in range(5):
        if x * y > 10:
            pairs.append((x, y))
```

### Generators

Rules:

- Use generators when values can be produced lazily.
- A generator docstring uses `Yields:`.
- If a generator manages an expensive resource, make cleanup explicit.
- Do not keep resource lifetime implicit in a partially consumed generator.

Good:

```python
def iter_prompt_text(examples: Iterable[PromptExample]) -> Iterable[str]:
    """Yield prompt text values.

    Yields:
        Prompt text values.
    """
    for example in examples:
        yield example.prompt
```

## Classes

### Class design

Rules:

- Prefer functions and data structures unless a class owns real state,
  invariants, or behavior.
- Keep related classes together when they form one cohesive contract, including
  schemas, exceptions, protocols, and their input/output records.
- Split modules by independent responsibilities, not by class count.
- Do not create classes only to group static functions.
- Do not use banned role words such as `Manager`, `Processor`, or `Helper`
  unless [`NAMING.md`](NAMING.md) identifies an explicit configured exception.
- Decide deliberately which attributes are public and which are internal.
- Use public attributes for simple data.
- Use one leading underscore for internal attributes.
- Avoid double-leading underscores unless protecting a base class from subclass
  name collisions.
- Focus on the shape of data before adding behavior.
- If a function coordinates work between multiple classes and no polymorphism is
  involved, keep it a function unless one class clearly owns the behavior.

Bad:

```python
class RuntimeManager:
    """Class that manages runtime work."""
```

### Initialization and named constructors

Rules:

- Keep `__init__` small.
- Pass `__init__` the values that the class needs. Do not pass complex external
  objects only because they contain those values.
- Do not couple a class constructor to API payloads, CLI namespaces, or provider
  software development kit response objects.
- Use classmethod named constructors for external representations, such as
  `from_payload`, `from_token`, or `from_path`.
- Do not construct business objects with `ClassName(**external_attributes)` when
  that couples the class to an external storage or wire format.
- Validation of class invariants belongs in initialization.
- Keep complex reading, serialization, deserialization, and validation systems
  outside the business object.
- Keep derived attributes cheap, deterministic, and based on initialized fields.
  Prefer a named constructor when deriving them requires I/O, external services,
  or complex parsing.

Good:

```python
@dataclass
class Point:
    """Two-dimensional point."""

    x: float
    y: float

    @classmethod
    def from_payload(cls, payload: PointPayload) -> Point:
        """Build a point from a validated payload."""
        return cls(x=payload.x, y=payload.y)
```

Bad:

```python
class Point:
    def __init__(self, database_row):
        self.x = database_row.x
        self.y = database_row.y


point = Point(**row.attributes)
```

### Dataclasses

Rules:

- Use dataclasses for plain data records.
- Keep dataclass fields typed.
- Document public fields in the class docstring `Attributes:` section when the
  class is public.
- Do not add methods to a dataclass unless they are part of the data contract.
- Do not use a dataclass as a disguised mutable global configuration object.
- Use `field(default_factory=...)` for mutable defaults.
- Use `__post_init__` for simple invariant checks or cheap derived fields.
- Prefer a named constructor over `__post_init__` when construction needs
  parsing, I/O, external objects, or multiple alternate sources.

Good mutable default:

```python
@dataclass
class Batch:
    """Batch of prompts."""

    prompts: list[PromptExample] = field(default_factory=list)
```

Bad mutable default:

```python
@dataclass
class Batch:
    prompts: list[PromptExample] = []
```

### Properties

Rules:

- Use properties only for cheap, straightforward, unsurprising attribute access.
- Do not use a property only to get and set an internal attribute.
- Do not hide expensive work behind attribute syntax.
- Do not hide side effects behind properties.
- Use `@property`; do not manually implement descriptors unless the power
  feature is necessary.
- Avoid properties for computations subclasses may need to override and extend.

Good:

```python
@property
def num_examples(self) -> int:
    """The number of examples."""
    return len(self.examples)
```

### Inheritance

Rules:

- Design explicitly for inheritance or avoid inheritance.
- Prefer composition over inheritance for code sharing.
- Do not subclass only to reuse methods or state.
- Do not use the template method pattern as a default design. A base class that
  defines control flow and calls subclass hooks can hide execution order.
  Prefer direct calls between the functions that own the operations.
- Do not mix three different inheritance purposes in one hierarchy: code
  sharing, interface definition, and specialization.
- Use protocols or small ABCs for interfaces.
- Use specialization only when the subclass truly is the base class plus more
  and can be used anywhere the base class is expected.
- Follow the Liskov substitution principle: callers that accept the base class
  must be able to interact correctly with the subclass.
- Keep strict specialization hierarchies shallow and physically close together
  when practical.
- Do not model variants as one class with a type field and many optional fields
  that only apply for some type values.
- Make invalid states unrepresentable where practical.
- Use composition when behavior varies across more than one axis.
- Put required tracking, caching, and timing in the operation that owns
  them. Do not add a forwarding class or wrapper only to attach them.
- Consider `functools.singledispatch` when an operation varies by type but does
  not clearly belong to one class.
- Public attributes have no leading underscore.
- Internal attributes use one leading underscore.
- Double-leading underscores are only for avoiding accidental subclass name
  collisions.
- If a class is intended for subclassing, document the public API and subclass
  API separately when that distinction matters.

Good specialization:

```python
@dataclass
class EmailAddress:
    """Email address shared by all address types."""

    id: UUID
    address: str


@dataclass
class Mailbox(EmailAddress):
    """Email address that stores mail."""

    password_hash: str
```

Bad optional-field variant:

```python
@dataclass
class EmailAddress:
    kind: str
    id: UUID
    address: str
    password_hash: str | None
    forwarding_targets: list[str] | None
```

### Decorators

Rules:

- Use decorators when they remove real repetition or express a clear framework
  contract.
- Decorator behavior must be unsurprising.
- Decorators run at definition time, usually import time. Do not let them depend
  on files, sockets, network calls, or other unavailable resources.
- Preserve function metadata in decorators that wrap functions.
- Avoid `staticmethod`. Use a module-level function instead.
- Use `classmethod` for named constructors or class-specific routines.
- Use `@property` only under the property rules above.

Good:

```python
class ModelConfig:
    @classmethod
    def from_name(cls, name: str) -> ModelConfig:
        """Build a model config from a variant name."""
        return cls(name=name)
```

Bad:

```python
class ModelConfig:
    @staticmethod
    def normalize_name(name: str) -> str:
        return name.strip().lower()
```

Use a module function:

```python
def normalize_model_name(name: str) -> str:
    return name.strip().lower()
```

### Exceptions as classes

Rules:

- Custom exceptions inherit from `Exception`.
- Do not inherit directly from `BaseException`.
- Exception class names use `PascalCase`.
- Error exception names end with `Error`.
- Do not repeat the module name in an exception name.
- Exception docstrings describe the represented condition.

Good:

```python
class InvalidVariantError(Exception):
    """The requested model variant is not supported."""
```

Bad:

```python
class VariantsInvalidVariantError(BaseException):
    """Raised in variants.py when the variant is invalid."""
```

## Exceptions and error handling

Rules:

- Use built-in exception classes when they fit the error.
- Raise `ValueError` for invalid argument values.
- Raise `TypeError` for invalid argument types when type validation is needed.
- Keep `try` blocks as small as possible.
- Catch specific exceptions.
- Do not use bare `except:`.
- Do not catch `Exception` unless re-raising or creating a deliberate isolation
  boundary that records and suppresses failures.
- Use `else` when code runs only if the `try` block succeeds.
- Use `finally` for cleanup that must run regardless of success or failure.
- Do not use `return`, `break`, or `continue` in a `finally` block when an
  exception could be active.
- Use `raise NewError(...) from error` when replacing an exception but preserving
  the cause.
- Use `raise NewError(...) from None` only when deliberately suppressing an
  irrelevant implementation exception, and preserve relevant details in the new
  message.
- When catching operating-system errors, prefer Python's explicit OSError
  subclass hierarchy over checking `errno` manually.

Good:

```python
try:
    value = collection[key]
except KeyError:
    return build_missing_key_result(key)
else:
    return build_result(value)
```

Bad:

```python
try:
    return build_result(collection[key])
except KeyError:
    return build_missing_key_result(key)
```

Good exception replacement:

```python
try:
    raw_value = payload["label"]
except KeyError as error:
    raise ValueError("Missing required field: label") from error
```

Bad catch-all:

```python
try:
    start_server()
except Exception:
    return None
```

## Assertions

Rules:

- Do not use `assert` for application logic, input validation, permission
  checks, or required preconditions.
- Do not rely on `assert` to satisfy type checking or runtime correctness.
- `assert` is acceptable for non-critical internal consistency checks where
  removing it would not change application behavior.
- Use explicit `if` checks and raise exceptions for real validation.

Good:

```python
def connect_to_port(minimum: int) -> int:
    """Connect to the next available port."""
    if minimum < 1024:
        raise ValueError(f"Minimum port must be at least 1024: {minimum=}")
    port = find_next_open_port(minimum)
    if port is None:
        raise ConnectionError(f"Could not connect on or above port: {minimum=}")
    assert port >= minimum
    return port
```

Bad:

```python
def connect_to_port(minimum: int) -> int:
    assert minimum >= 1024
    port = find_next_open_port(minimum)
    assert port is not None
    return port
```

## Boolean logic and comparisons

Rules:

- Compare to `None` with `is None` or `is not None`.
- Do not compare booleans to `True` or `False`.
- Use truthiness for sequences and containers.
- When handling integers, compare to `0` when zero has domain meaning.
- Do not write `if not value` when `None`, `0`, `False`, and empty containers
  have different meanings.
- Use `is not` instead of `not ... is`.
- Use `isinstance()` for type checks.
- Use `startswith()` and `endswith()` for prefix and suffix checks.
- Do not compare types directly unless exact type identity is the real contract.
- For rich ordering, implement all relevant comparison operations or use
  `functools.total_ordering()`.

Good:

```python
if value is not None:
    ...

if not examples:
    ...

if count == 0:
    ...

if isinstance(obj, int):
    ...

if filename.endswith(".json"):
    ...
```

Bad:

```python
if value != None:
    ...

if greeting == True:
    ...

if len(examples) == 0:
    ...

if type(obj) is int:
    ...

if filename[-5:] == ".json":
    ...
```

NumPy arrays may reject implicit boolean evaluation. Use `.size` or another
explicit property when checking array emptiness.

## Control flow simplification

Rules:

- Reduce nesting when a condition can be merged without changing behavior.
- Merge adjacent `if` statements when the inner condition has no intervening
  work and no `else` branch that changes the result.
- Prefer guard clauses when they remove a level of nesting and keep the main
  path easy to scan.
- Hoist repeated code out of conditional branches when it runs in every branch.
- Hoist loop-invariant statements out of `for` and `while` loops when they do
  not depend on the loop variable and have no required repeated side effect.
- Do not combine conditions when separate conditions communicate distinct
  domain decisions more clearly.
- Do not hoist code when execution order, exceptions, timing, external
  calls, or mutation would change.

Good merged condition:

```python
if is_enabled and has_examples:
    return build_examples()
```

Bad nested condition:

```python
if is_enabled:
    if has_examples:
        return build_examples()
```

Good hoisted branch code:

```python
if sold > DISCOUNT_AMOUNT:
    total = sold * DISCOUNT_PRICE
else:
    total = sold * PRICE
label = f"Total: {total}"
```

Bad repeated branch code:

```python
if sold > DISCOUNT_AMOUNT:
    total = sold * DISCOUNT_PRICE
    label = f"Total: {total}"
else:
    total = sold * PRICE
    label = f"Total: {total}"
```

Good loop-invariant hoist:

```python
city = "London"
for building in buildings:
    addresses.append((building.street_address, city))
```

Bad loop-invariant assignment:

```python
for building in buildings:
    city = "London"
    addresses.append((building.street_address, city))
```

Do not merge conditions when it hides separate decisions:

```python
if not request.user:
    raise PermissionError("Authentication is required")
if not request.user.can_export:
    raise PermissionError("Export permission is required")
```

## Iteration and collections

Rules:

- Use default iterators and membership operators for containers that support
  them.
- Iterate dictionaries directly for keys.
- Use `.items()` when both keys and values are needed.
- Do not call `.keys()` only to iterate keys.
- Do not call `.readlines()` only to iterate file lines.
- Do not mutate a container while iterating over it.
- Prefer clear loops over dense collection transformations.
- Use `yield from iterable` instead of a loop that only yields every item from
  another iterable.
- Use `any()` and `all()` for simple existence or universal predicate checks.
- Use `[]` for an empty list and `{}` for an empty dictionary.
- Use `list()` or `dict()` when converting an iterable or mapping, not for empty
  literals.

Good:

```python
for key in values:
    ...

for key, value in values.items():
    ...

for line in file_obj:
    ...

if item in values:
    ...
```

Bad:

```python
for key in values.keys():
    ...

for line in file_obj.readlines():
    ...
```

Good delegated yield:

```python
def get_content(entry: Entry) -> Iterable[Block]:
    yield from entry.get_blocks()
```

Bad delegated yield:

```python
def get_content(entry: Entry) -> Iterable[Block]:
    for block in entry.get_blocks():
        yield block
```

Good predicate check:

```python
found = any(item == expected for item in items)
all_valid = all(is_valid(item) for item in items)
```

Bad predicate loop:

```python
found = False
for item in items:
    if item == expected:
        found = True
        break
```

Good empty containers:

```python
items = []
metadata = {}
```

Bad empty containers:

```python
items = list()
metadata = dict()
```

## Strings, logging, and error messages

### String formatting

Rules:

- Use f-strings, `%` formatting, or `.format()` for formatting.
- Prefer f-strings for ordinary string interpolation.
- Do not use `+` to format strings with values.
- A single `a + b` concatenation is allowed when both values are already strings
  and this is not formatting.
- Do not accumulate strings with `+` or `+=` in a loop.
- Accumulate parts in a list and `"".join(parts)`, or use `io.StringIO`.
- Use implicit literal concatenation inside parentheses for long string
  literals.

Good:

```python
message = f"name: {name}; score: {score}"

rows = ["<table>"]
for last_name, first_name in employees:
    rows.append("<tr><td>%s, %s</td></tr>" % (last_name, first_name))
rows.append("</table>")
employee_table = "".join(rows)
```

Bad:

```python
message = "name: " + name + "; score: " + str(score)

employee_table = "<table>"
for last_name, first_name in employees:
    employee_table += "<tr><td>%s, %s</td></tr>" % (last_name, first_name)
employee_table += "</table>"
```

### Logging

Follow [GENERAL.md](GENERAL.md#logging). Do not use the `logging` module,
third-party logging libraries, logging configuration, or `logger.exception()`.
Do not use `print()` or warnings as diagnostic logging substitutes.

Return values for successful operations. Raise specific exceptions when an
operation cannot complete, and handle expected failures at their owner boundary.
CLI entrypoints may convert failures to a concise error message and a nonzero
exit status without printing a traceback. Use `print()` only for output required
by the command's public contract.

### Error messages

Rules:

- Error messages must match the actual error condition.
- Interpolated values must be clearly identifiable.
- Prefer `name=value` formatting for values that aid debugging.
- Keep messages easy to grep.
- Start user-visible messages with an uppercase letter.
- Do not leak schema names, table names, file paths, internal IDs, stack traces,
  trigger names, policy names, secrets, or implementation details.
- Use generic messages for configuration and infrastructure failures.

Good:

```python
if not 0 <= probability <= 1:
    raise ValueError(f"Probability must be between 0 and 1: {probability=}")
```

Bad:

```python
if probability < 0 or probability > 1:
    raise ValueError(f"The probability was bad: {probability}")
```

Good error reporting around OS errors:

```python
try:
    workdir.rmdir()
except OSError:
    raise RuntimeError("Could not remove work directory") from None
```

Bad error reporting:

```python
try:
    workdir.rmdir()
except OSError:
    raise RuntimeError("Directory already was deleted") from None
```

The bad message assumes the reason for the failure. Describe the failed
operation accurately without exposing internal paths or emitting a traceback.

## Files and stateful resources

Rules:

- Explicitly close files, sockets, and similar stateful resources.
- Prefer `with` statements for resources that support context management.
- Use `contextlib.closing()` for closeable resources without context-manager
  support.
- Do not rely on finalizers or garbage collection for resource cleanup.
- Keep resource scope as small as practical.
- Do not return open resources from helpers unless resource ownership is part of
  the documented contract.
- Document resource lifetime when context-based management is infeasible.

Good:

```python
with path.open(encoding="utf-8") as file_obj:
    for line in file_obj:
        parse_line(line)
```

Bad:

```python
file_obj = path.open()
for line in file_obj:
    parse_line(line)
```

Good for closeable objects without context-manager support:

```python
import contextlib

with contextlib.closing(open_remote_resource(url)) as resource:
    consume(resource)
```

## Main programs and top-level code

Rules:

- Executable modules put main behavior in a `main()` function.
- Use `if __name__ == "__main__":` before executing program behavior.
- Prefer `raise SystemExit(main())` when `main()` returns an exit code.
- Do not parse CLI arguments at import time.
- Do not load models, make network calls, or mutate files at import time.
- Use `python -m package.module` for repository Python entrypoints.
- Shell scripts must call Python modules, not inline Python snippets.
- Files that are not intended to execute directly do not need a shebang.
- Directly executable Python files may use `#!/usr/bin/env python3` when a
  shebang is needed.

Good:

```python
def main() -> int:
    """Run the command."""
    ...
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Bad:

```python
args = parser.parse_args()
start_server(args)
```

## Packages and architecture

Rules:

- Keep packages shallow and purposeful.
- Flatten packages that contain only `__init__.py` and one other module, except
  for the configured folder-policy exceptions.
- Do not create another single-file package unless the folder policy explicitly
  permits it.
- Do not create import cycles.
- Do not create lazy module export hooks such as module-level `__getattr__`,
  `__dir__`, or `__getattribute__`.
- Do not use dynamic imports for lazy loading.
- Do not use package `__init__.py` files to hide expensive imports.
- Keep `__init__.py` files small and import-stable.
- Barrel `__init__.py` files may contain imports and `__all__`.
- Respect the dependency contracts enforced by the configured import checks.
- Keep lower-level packages independent of higher-level workflow packages.

### Package layout and import path

Rules:

- Respect the project's package structure. Keep runtime behavior and runtime
  settings separate from development tooling; runtime code must not import
  development packages.
- Group static defaults, limits, patterns, and configurable values by purpose.
  Include required configuration in the distribution.
- Keep application or framework entrypoints small. Follow the package's
  supported loading contract when choosing relative and absolute imports.
- Run Python entrypoints through the configured environment or `python -m`
  with the intended package context.
- Do not mutate `sys.path` or depend on the current working directory to make
  imports work.
- Isolated workers use an explicitly selected interpreter and an entrypoint
  their launcher can resolve independently of the current working directory.
- Enforce the project's declared dependency contracts. Lower-level settings,
  data, and discovery owners must not acquire dependencies on higher-level
  execution or integration code merely for convenience.

Keep cohesive modules together. Apply the single-module package policy in
[NAMING.md](NAMING.md#files-and-directories), including only explicit configured
exceptions. Do not add empty files or split cohesive code merely to satisfy a
folder count.

## Power features

Avoid power features unless the project already has a clear local pattern and
the feature is necessary.

Avoid:

- custom metaclasses;
- bytecode manipulation;
- dynamic inheritance;
- object reparenting;
- import hooks and import hacks;
- runtime monkeypatching;
- reflection-heavy designs;
- modifying interpreter internals;
- `__del__` cleanup logic;
- manual descriptor implementations;
- dynamic code generation.

Allowed standard-library uses include `dataclasses`, `enum`, and `abc` when they
fit the problem.

Rules:

- Do not use a power feature to make code shorter.
- Do not use a power feature to hide a dependency cycle or ownership problem.
- Prefer ordinary functions, dataclasses, explicit imports, and explicit data
  structures.

## Threading and concurrency

Rules:

- Do not rely on atomicity of built-in types.
- Do not rely on atomic variable assignment for synchronization.
- Use `queue.Queue` when threads exchange discrete items.
- Use `threading` locks, conditions, or higher-level primitives for shared
  state.
- Prefer `threading.Condition` over low-level polling loops.
- Keep shared mutable state small and explicit.
- Document concurrency, cancellation, and isolation behavior when present.

## External integration boundaries

- Keep registration small and free of network activity. Use documented
  framework APIs and native interchange types for supported data.
- Keep host- and provider-required identifiers exact. For requested changes to
  project-owned registration IDs, saved keys, or settings, update affected
  callers and examples together and migrate required stored data directly. Do not keep
  compatibility aliases or discard user data. A label-only edit changes no
  saved keys.
- Keep host imports at their boundary. Follow the isolated-worker and import
  requirements in [package layout](#package-layout-and-import-path).
- Validate decoded JSON at entry. Keep SDK typing uncertainty at the transport
  boundary; do not spread `Any` or blanket ignores into application code.
- Keep blocking file and media work off the host event loop. Bound queues,
  threads, memory, session duration, and cleanup time. Own, cancel, and await
  every created task; propagate cancellation after cleanup.
- Use verified external command schemas and resource names. Discovery lists
  available resources; it does not prove that each resource has a working
  application adapter.
- Validate refreshed discovery records separately and replace them atomically.
  Refresh must not execute provider text, install code, or open paid sessions.
- Keep credentials out of widgets, saved workflows, logs, and public files.
  Use the private credential store or environment configuration.
- Keep paid operations and billing changes within the explicitly authorized
  scope. A runtime check does not authorize buying credits, enabling top-ups,
  or changing account settings. Keep manual run records private.
- Preserve user documents, saved workflows, media, unrelated extensions, and
  browser tabs during manual checks. Use a separate browser session for
  unrelated web work.

## Manual verification

Follow [GENERAL.md](GENERAL.md#verification-scope) for authorization and scope.
For requested runtime checks, use the installed distribution in its supported
runtime. Exercise the affected behavior with real inputs. Include cancellation
and cleanup when relevant. Keep results private and report only what was checked.

## Verification commands

Follow [GENERAL.md](GENERAL.md#verification-commands). Find the project's actual
commands in its task configuration and package metadata before invoking them;
do not assume a task name, optional dependency group, source directory, or CLI
flag from another project.

For requested Python verification:

- Use the configured formatter and linter for formatting and code policy.
- Use the configured type checker for type contracts.
- Use the configured import and structural checks for dependency boundaries,
  module layout, naming, and documentation coverage.
- Prefer the project command for the requested category unless the user asks
  for a narrower tool or file scope.
- Use the configured environment and supported command arguments. Do not invent
  dependency groups, rewrite import paths, or bypass the package loading contract
  merely to make a check run.

## Review checklist

Before finishing Python changes, review the diff for these points:

- Does the code follow local project rules over generic style preferences?
- Are imports top-level, grouped, sorted, and free of cycles?
- Is the module import-stable, with no import-time work?
- Are public APIs typed and documented?
- Do argument types accept the broadest useful protocol or abstract collection?
- Do concrete implementations return concrete types?
- Is `Any` avoided where `object`, a protocol, or a type variable would express
  the contract?
- Are names consistent with [`NAMING.md`](NAMING.md)?
- Are functions small, focused, and under the local length limit?
- Are defaults immutable or initialized inside the function?
- Are None checks explicit?
- Are constructors free of external row, payload, SDK, or CLI object coupling?
- Is subclassing used only for interfaces or true specialization, not code
  sharing?
- Are exceptions specific, with narrow `try` blocks?
- Are resources managed with `with` or documented ownership?
- Does the code avoid logging, logging configuration, and stack-trace output
  as required by [GENERAL.md](GENERAL.md#logging)?
- Are error messages precise, actionable, and free of internal details?
- Are environment variables read, parsed, and validated at a boundary instead
  of inside business logic?
- Are comments present where behavior is non-obvious and absent where they only
  narrate code?
- Is `__all__` explicit and at the bottom when public exports exist?
- Are package boundaries and import-linter contracts respected?
- Does importable code respect the package layout without `sys.path` mutation?
- Does verification follow [GENERAL.md](GENERAL.md#verification-scope)?

## Anti-patterns

Do not write:

```python
from module import *
```

```python
from typing import Dict, List, Type, Union, Optional
```

```python
type Rows = list
```

```python
def format_value(value: Any) -> str:
    return str(value)
```

```python
def read_lines(path: None | Path) -> list[str]: ...
```

```python
_Rows = list[dict[str, object]]
```

```python
Path: TypeAlias = pathlib.Path
```

```python
def f(value=[]): ...
```

```python
if value == None:
    ...
```

```python
if flag == True:
    ...
```

```python
try:
    ...
except:
    ...
```

```python
try:
    return transform(collection[key])
except KeyError:
    return fallback()
```

```python
logger.info(f"Loaded {count} prompts")
```

```python
logging.info("Loaded %d prompts", count)
```

```python
logger.exception("Upload failed")
```

```python
STATE = {"instance": None}
```

```python
def get_instance(): ...
```

```python
def build():
    import examples
```

```python
def build_client() -> Client:
    token = os.getenv("API_TOKEN", "example-token")
    return Client(token=token)
```

```python
import importlib

module = importlib.import_module("examples")
```

```python
import sys

sys.path.insert(0, "src")
```

```bash
python -m pip install -r loose-requirements.lock
python -m pip install --extra-index-url https://packages.example.com/simple private-package
python setup.py install
python setup.py develop
easy_install example-package
```

```python
def __getattr__(name: str) -> object: ...
```

```python
class TrainingManager: ...
```

```python
class Point:
    def __init__(self, row):
        self.x = row.x
        self.y = row.y
```

```python
class BaseRepository(abc.ABC):
    def add_product(self, product: Product) -> None:
        self._add_product(product)
        self.seen.add(product)
```

```python
double = lambda value: value * 2
```

```python
employee_table = ""
for row in rows:
    employee_table += render_row(row)
```

```python
if len(examples):
    ...
```

```python
if type(value) is str:
    ...
```

```python
if name[:4] == "test":
    ...
```

```python
def main(): ...


main()
```

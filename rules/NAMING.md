# Naming

This is the single source of truth for naming in this repository. It covers
general naming principles plus Python, Bash, TypeScript, framework integrations,
external providers, and user-visible content.

Use this file together with the automated checks. This document explains how to
choose names. The local tooling enforces the concrete policy.

## Contents

- [Authority and local enforcement](#authority-and-local-enforcement)
- [General naming rules](#general-naming-rules)
- [Vocabulary and role words](#vocabulary-and-role-words)
- [Functions and methods](#functions-and-methods)
- [Booleans and predicates](#booleans-and-predicates)
- [Files and directories](#files-and-directories)
- [Python](#python)
- [Bash](#bash)
- [TypeScript](#typescript)
- [HTML, CSS, and content](#html-css-and-content)
- [Data, models, and external boundaries](#data-models-and-external-boundaries)
- [Review checklist](#review-checklist)

## Authority and local enforcement

Naming decisions must satisfy both this guide and the local quality tooling.

Rules:

- Follow this file when naming files, directories, modules, packages, classes,
  dataclasses, functions, methods, parameters, variables, and constants.
- Also follow it when naming CLI flags, environment variables, data examples,
  and documentation examples.
- Follow the project's configured language naming checks and structural checks
  for prefix collisions, package structure, and import layout.
- Keep banned vocabulary and narrow language or external-boundary exceptions
  in the project's configured naming policy; do not require a particular tooling
  directory or implementation.
- Treat local lint failures as authoritative. If this guide and tooling disagree,
  fix the disagreement instead of working around it locally.
- Do not bypass naming policy by hiding bad names in string keys, aliases,
  generated wrappers, or CLI flags.
- Provider-owned names may keep provider spelling when the applicable language
  policy records the boundary. Hand-written wrappers around them must follow
  this guide.

## General naming rules

Names are a design tool. A name lets a reader understand the concept,
scope, role, and expected value without reading the implementation first.

Rules:

- Name by role, responsibility, and domain meaning.
- Do not name by storage type, library type, collection shape, or implementation
  accident.
- Use English unless representing an external identifier that must keep another
  spelling.
- Prefer the shortest name that is still clear at the use site.
- Add qualifiers only when the unqualified name is genuinely ambiguous.
- Avoid private shorthand that only the original author understands.
- Avoid contractions created by deleting letters from a word.
- Do not duplicate context already supplied by the enclosing module, directory,
  class, or package.
- Do not encode every implementation detail in a name.
- Use the same vocabulary for the same concept across the repository.
- Use singular names for single values and plural names for collections.
- Name collections by their contents, not by the collection type.
- Use role words when primitive or weak types do not carry enough meaning.
- Preserve required external names at boundaries, but translate them into domain
  names before they move inward.
- Do not use the terms banned by the configured naming policy for local names.
  Apply only its narrow, documented language or external-boundary exceptions.
- Use a precise verb such as `read`, `choose`, `derive`, `build`, `create`,
  `parse`, `validate`, `sanitize`, or `format` only when it describes the real
  operation.

### Role instead of type

Names explain what the value means in the domain.

Bad:

```python
data = encode_prompt(text)
dict_value = compute_latency_stats(examples)
bool_value = camera.is_available()
```

Good:

```python
encoded_input = encode_prompt(text)
latency_stats = compute_latency_stats(examples)
is_camera_available = camera.is_available()
```

### Avoid redundant context

Let the owner provide context. Add context only when the name would otherwise be
ambiguous outside the owner.

Bad:

```python
@dataclass
class PromptMessage:
    prompt_message_text: str
    prompt_message_role: str
```

Good:

```python
@dataclass
class PromptMessage:
    text: str
    role: str
```

### Avoid type and shape duplication

Do not repeat information already expressed by the type system or declaration.

Bad:

```python
name_string: str = variant.name
messages_list: list[Message] = parse_messages(payload)
config_dict: dict[str, object] = build_config()
```

Good:

```python
name: str = variant.name
messages: list[Message] = parse_messages(payload)
runtime_config: dict[str, object] = build_config()
```

### Avoid vague and inflated words

Do not use vague words to avoid naming the real responsibility.

Bad:

```text
model_utils.py
data_helper.py
runtime_manager.py
common.py
base_processor.py
```

Good:

```text
capture.py
credentials.py
runtime.py
paths.py
latency_stats.py
```

The banned-terms file includes `Helper`, `Helpers`, `Util`, `Utils`, `Common`,
`Core`, `Manager`, and `Processor`.
Use one of these terms only when the applicable language policy contains an
explicit exception for that name and location.

## Vocabulary and role words

Choose role words deterministically. A deterministic suffix tells a reader what
kind of boundary or owner they are looking at.

Use these meanings consistently:

| Role word   | Use when                                                                  |
| ----------- | ------------------------------------------------------------------------- |
| `Config`    | A value or module owns configuration for a cohesive area.                 |
| `Example`   | One concrete example in documentation or sample input.                    |
| `Model`     | A model object, supported model name, or artifact.                        |
| `Variant`   | A documented version of a provider model.                                 |
| `Client`    | External API, software development kit, filesystem, or platform boundary. |
| `Parser`    | Converts raw input into structured data.                                  |
| `Validator` | Checks a value and returns or raises validation failure.                  |
| `Formatter` | Converts a value into display or wire text.                               |
| `Runner`    | Owns a top-level command workflow.                                        |
| `Result`    | A completed operation's structured output.                                |
| `Stats`     | Aggregated measurements or counters.                                      |

`Runner` is a role for the owner of a top-level command workflow. It does not
make `run` an acceptable generic function name.

Do not use a suffix only because a name feels too short. If the role is not
real, rename the symbol to the concrete domain concept.

Bad:

```python
class RuntimeManager: ...


def process(data): ...
```

Good:

```python
class RecordingSession: ...


def build_examples(source_items): ...
```

## Functions and methods

Function and method names describe the action and the domain item being
acted on without repeating context already supplied by the owner.

Rules:

- Start with the action unless a framework convention requires another shape.
- Include enough domain context to read clearly at the call site.
- Do not use generic names such as `process`, `handle`, `run`, `execute`,
  `manage`, `perform`, or `do_work` when the action can be named.
- Use `handle` only for callbacks, framework/event boundaries, or signal
  handlers.
- Start every function with one verb from the table below, with the meaning
  the table gives it. Predicates start with `is_` or `has_`. The function
  policy checks this for `src/`, `scripts/`, and the package `__init__.py`.
- Avoid positional boolean parameters. Use options, enums, or explicit function
  names when a boolean would be ambiguous.

### Verbs used in this repository

| Verb                  | Meaning                                                                       |
| --------------------- | ----------------------------------------------------------------------------- |
| `read`                | Bring a value from disk, a preset, a prompt file or ComfyUI into memory.      |
| `save`                | Write to disk.                                                                |
| `send`                | Make a network or provider call.                                              |
| `parse`               | Turn text or a payload into a record.                                         |
| `build`               | Make a value from other values already in memory.                             |
| `create`              | Make a new durable or independent value.                                      |
| `choose`              | Pick one value from inputs, defaults and constraints.                         |
| `list`                | Pick or enumerate many.                                                       |
| `find`                | Look one up by key; may report absence.                                       |
| `plan`                | Decide an order or a dependency before any call.                              |
| `rank`                | Return a sort key.                                                            |
| `validate`            | Check and raise.                                                              |
| `describe`            | Turn a value into prose for a person.                                         |
| `format`              | Turn a value into display or wire text.                                       |
| `get`, `set`, `reset` | Immediate access without work or I/O, direct assignment, return to the start. |
| `decode`, `encode`    | Bytes or serialized payloads to typed values, and back.                       |
| `sanitize`            | Transform input into a safe external form.                                    |
| `wait`                | Await a task, a thread, or a job until it settles.                            |
| `register`            | Hand a route or a hook to the host that calls it.                             |
| `delete`              | Remove a file or a record.                                                    |
| `download`            | Read a file or a document from a network address.                             |
| `measure`             | Compute a size or a length.                                                   |
| `place`               | Set positions in a layout.                                                    |

Bad:

```python
def process(value): ...


def handle_data(data): ...


def run(model_name, output_dir): ...
```

Good:

```python
def validate_prompt(text, max_length): ...


def build_examples(source_items): ...
```

### One concept per function name

If the function name needs `and`, `or`, `with`, `plus`, or a vague umbrella verb,
the function may own too many concepts.

Bad:

```python
def validate_and_upload_image(image, session): ...
```

Good:

```python
def validate_image(image): ...


def upload_image(image, session): ...
```

### Boundary names

At boundaries, name the conversion explicitly.

Bad:

```python
def transform(item): ...
```

Good:

```python
def build_example(raw_item): ...


def parse_model_name(candidate): ...
```

## Booleans and predicates

Boolean names must read as assertions at the use site.

Rules:

- Use `is_` for state or characteristics.
- Use `has_` for possession or presence.
- Use `can_` for capability.
- Do not introduce `should_` in local names. Preserve that spelling at an
  external framework boundary only when the applicable language policy records
  the exception.
- Avoid negative names such as `is_not_ready` when the positive form is clearer.
- Do not name booleans like nouns that could be non-boolean values.
- Prefer the boolean name that matches the branch without double negation.

Exception: a boolean widget ID that a person reads as a checkbox label, such as
`recursive`, `descending` or `captions`, keeps the label's spelling, and the
`execute` parameter that receives it keeps the same name because ComfyUI calls
the node by input ID. Record fields and parameters that only code reads take
`is_`, `has_` or `can_`.

Bad:

```python
remote = args.remote
token = credential.is_available()
not_ready = status != "ready"
```

Good:

```python
is_remote = args.remote
has_credential = credential.is_available()
is_ready = status == "ready"
```

Bad:

```bash
ready='false'
if [[ "${ready}" != 'true' ]]; then
  fail 'Not ready'
fi
```

Good:

```bash
is_ready='false'
if [[ "${is_ready}" != 'true' ]]; then
  fail 'Not ready'
fi
```

## Files and directories

Files and directories define ownership. Name them for the behavior or entity
they own, not for reuse intent.

Rules:

- Python source filenames use `snake_case.py`, except Python-owned files such as
  `__init__.py` and `__main__.py`.
- Flatten Python packages containing `__init__.py` and exactly one non-init
  module unless the configured folder policy explicitly permits the package.
  Do not manufacture files to meet a folder count.
- Python sibling filename prefixes must be unique unless the quality policy
  explicitly configures an exception.
- Bash files in the same directory must not share the first filename component
  before `_` or `-`.
- Related script families own a subdirectory instead of accumulating prefixed
  sibling files.
- Quality modules are named for the rule or workflow they enforce, regardless
  of where the project keeps its tooling.
- Do not create catch-all files or directories for unrelated code.
- Do not move code into shared locations only because a future caller might
  appear.
- Promote shared code only when there is a repeated concept and a stable owner.
- A directory named by a broad layer is acceptable only when the project
  architecture explicitly owns that layer.

Bad:

```text
src/helpers.py
src/utils.py
src/models.py
src/misc.py
scripts/do_stuff.sh
```

## Python

Python naming follows PEP 8 where it fits these rules, together with the
project's configured naming checks.

### Python case rules

Rules:

- Modules and packages use `snake_case`.
- Functions, methods, variables, and parameters use `snake_case`.
- Classes, dataclasses, and exception types use `PascalCase`.
- Constants use `UPPER_SNAKE_CASE`.
- CLI flags use lowercase `kebab-case`, such as `--model-name` and
  `--output-dir`.
- Environment variables use `UPPER_SNAKE_CASE`.
- Avoid one-letter names except conventional uses covered by the naming policy,
  such as `i`, `j`, or `k` in a short loop and `x` or `y` for coordinates.
- Exceptions end with `Error` when they represent errors.
- Type aliases use `PascalCase`, with one leading underscore for internal aliases.
- Private unconstrained type variables may use `_T` and `_P`.
- Never use `l`, `O`, or `I` as single-character names.
- Use `self` for instance methods and `cls` for class methods.
- If a parameter conflicts with a keyword, append one trailing underscore.
- Preserve provider capitalization in external names.

Bad:

```python
class tool_dataset: ...


MAXLEN = 512


def BuildExamples(data): ...
```

Good:

```python
class RuntimeConfig: ...


MAX_LENGTH = 512


def build_examples(source_items): ...
```

### Python modules and imports

Rules:

- Keep import aliases rare. Use aliases only for standard, widely understood
  conventions or real collision avoidance.
- Named imports keep their exported name unless a collision forces an alias.
- If aliasing is required, use a domain or module component that explains the
  collision.
- Keep `__all__` names accurate and ordered according to local lint rules.

Bad:

```python
from src.runtime.config import ModelSettings as Thing
```

Good:

```python
from src.runtime.config import ModelSettings
```

### Python types and dataclasses

Rules:

- Dataclass names describe the domain value they represent.
- Field names describe the value inside the owning type without repeating the
  type name.
- Use `Path` variables with names that reveal whether they point to a directory,
  file, model, result, or repository root.
- Use `*_path` for filesystem paths and `*_dir` only for directories.
- Use `*_id` only for real identifiers, not arbitrary names or labels.
- Use `*_name` for display or provider names.
- Use `*_key` for dictionary keys and supported variant keys.

Bad:

```python
@dataclass
class EvalExample:
    eval_example_text: str
    eval_example_result: str
```

Good:

```python
@dataclass
class EvalExample:
    text: str
    prediction: str
```

### Python boundary names

Rules:

- Keep raw provider or CLI names at the boundary.
- Translate external names into domain names before passing values inward when
  the external name is not the domain concept.
- Keep provider credential lookup inside the credential boundary.
- Keep path construction in config/path owners rather than rebuilding paths in
  business logic.
- Name functions that cross boundaries for the operation they perform.

## Bash

Bash naming follows Google shell guidance where it fits this repository.

### Bash case rules

Rules:

- Shell source file stems use lowercase words separated by hyphens or
  underscores.
- Task-runner entrypoints and Git hooks keep the names required by their tools,
  including extensionless names where required.
- Other executable shell scripts use `.sh`.
- Sourced libraries use `.sh` and are not executable.
- Functions and mutable variables use `lower_snake_case`.
- Function-local variables use `lower_snake_case`.
- Constants, readonly values, exported environment variables, and externally
  configured values use `UPPER_SNAKE_CASE`.
- Do not use the `function` keyword for new functions. Use `name() { ...; }`.

Good:

```text
main.sh
lint.sh
quality.sh
report.sh
```

Good:

```bash
package_prepare() {
  local output_dir="$1"
}
```

### Bash variables

Rules:

- Loop variables describe the item being iterated.
- Use `tmp_dir` or `tmp_file` only for actual temporary filesystem paths.
- Avoid vague names when a domain name is available.
- Avoid shell-reserved and shell-special names for unrelated values.
- Initialize variables before use.
- Prefer explicit empty strings or arrays over relying on unset variables.
- Declare function-specific variables with `local`.
- Separate `local`, `declare`, `readonly`, and `export` from command
  substitutions when the command status matters.

Bad:

```bash
X=/tmp/a
for i in "${things[@]}"; do
  do_it "${i}"
done

local output="$(generate_results)"
```

Good:

```bash
readonly WORKFLOWS_DIR="${ROOT_DIR}/workflows"

for workflow_file in "${workflow_files[@]}"; do
  validate_workflow "${workflow_file}"
done

local result_output
result_output="$(generate_results)" || return 1
```

### Bash functions

Rules:

- Private functions begin with `_` and are callable only inside their defining
  file.
- Public sourced functions begin with their family or domain namespace,
  followed by the action, such as `server_start`, `restart_read_state`, or
  `package_prepare`.
- Entrypoint-local functions are private except for `main`.
- Within the owner namespace, function names use verb phrases when the function
  has side effects.
- Name functions that print to standard output for the data they print.
- Validation functions return a status and report failures through their
  defined error contract. Follow [GENERAL.md](GENERAL.md#logging).
- Do not name scripts or functions after shell builtins or common commands.
- Do not make function names so generic that callers and local check findings
  lose context.

Bad:

```bash
test() {
  ...
}

run() {
  ...
}

process() {
  ...
}
```

Good:

```bash
venv_python() {
  ...
}

package_prepare() {
  ...
}

model_validate_dir() {
  ...
}
```

### Bash environment names

Rules:

- Environment variables are `UPPER_SNAKE_CASE`.
- Export only variables child processes need.
- Do not overwrite important shell environment names casually.
- Validate configured environment variable names before using indirect
  expansion.
- Name required environment values by the external contract when the runtime or
  provider platform owns the name.

Bad:

```bash
export token="${TOKEN}"
name="$1"
printf '%s\n' "${!name}"
```

Good:

```bash
export APP_DATA_DIR="${APP_DATA_DIR}"

env_name="$1"
if [[ ! "${env_name}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
  printf 'Error: invalid environment variable name\n' >&2
  return 1
fi
printf '%s\n' "${!env_name}"
```

## TypeScript

These naming rules apply to TypeScript source and tooling.

### TypeScript case rules

Rules:

- Functions, parameters, mutable variables, and normal constants use
  `lowerCamelCase`.
- Classes use `PascalCase` only when instance identity is real.
- Static constant properties and environment-owned names may use
  `UPPER_SNAKE_CASE`.
- Object properties use `lowerCamelCase` unless they mirror an external
  contract.
- Unused parameters start with `_`.
- Do not use leading underscores for privacy. Keep private values local to the
  module.
- Do not use all-capital names for ordinary local constants.

Bad:

```typescript
const SETTINGS = readSettings();
function Build_Dialog(settings_value: Settings): void {}
const _privateValue = true;
```

Good:

```typescript
const settings = readSettings();
function buildDialog(settings: Settings): void {}
const isEnabled = true;
```

### TypeScript files

Rules:

- Name module files for the concept they own.
- Prefer nouns for data and configuration modules. Use verbs for small
  executable scripts only when the file acts as a command.
- Do not use generic filenames such as `helpers.ts`, `utils.ts`, `index.ts`,
  `common.ts`, and `misc.ts`.
- Keep behavior with its established owner. Name modules for the responsibility
  they actually own rather than creating a new owner for a naming change.

Bad:

```text
web/utils.ts
web/shared/helpers.ts
web/settings/helpers.ts
```

Good:

```text
web/help/links.ts
web/settings/api.ts
web/live/controls.ts
```

### TypeScript functions

Rules:

- Use verbs for functions that perform work: `build`, `copy`, `display`,
  `validate`, and `write`.
- Use nouns for returned values only when the function name still reads as an
  action, such as `readPackageName`.
- Use `is`, `has`, or `can` for boolean-returning functions.
- Name boundary functions for the boundary they own, such as `readSettings`,
  `buildHelp`, or `sendCommand`.
- Avoid pass-through names that only restate another function.

Bad:

```typescript
function doStuff(input: Input): void {}
function process(data: Data): void {}
function check(value: Value): void {}
```

Good:

```typescript
function buildHelp(page: Page): void {}
function buildNodeHelp(markdown: string): void {}
function isConnected(session: Session): boolean {
    return session.connected;
}
```

### TypeScript modules and exports

Rules:

- Prefer named exports for reusable module code.
- Avoid default exports in project-owned modules unless a tool requires one.
- Do not create namespace objects only to group functions.
- Do not export mutable variables as a module contract.
- Import the owning leaf module instead of a broad barrel.

Bad:

```typescript
export default {
    buildPage() {},
};
```

Good:

```typescript
export function buildPage(page: Page): Page {
    return page;
}
```

## HTML, CSS, and content

Name interface controls, styles, and help files for the component or task
they describe.

Rules:

- Data attributes use kebab-case because they are HTML attributes.
- CSS classes describe the component or state they style.
- CSS custom properties use kebab-case and identify the value's role.
- When help lookup uses registered component IDs as filenames, match the exact
  registered ID rather than deriving filenames from display labels.
- Do not hide user-visible copy in variable names or comments. Put copy in the
  owning component or authored guide.

Bad:

```html
<div data-deviceClass="phone"></div>
```

Good:

```html
<div data-device-class="phone"></div>
```

## Data, models, and external boundaries

Keep identifiers required by framework and provider APIs exact.

Rules:

- Keep provider model identifiers and provider spellings exact.
- Keep public registration IDs stable and independent of mutable display
  labels. Use a namespace when the registry requires one or shared registration
  would otherwise collide.
- Follow the interface's established display-label conventions. Do not impose
  a project-specific prefix or suffix on every integration.
- Keep framework callback names and required provider method names exact.
- Follow [documentation casing](DOCUMENTATION.md#use-title-case-for-document-titles)
  for visible content, preserving exact external labels.
- Keep visible labels in schemas and workflow notes consistent.
- Name example workflows by family, two-digit number and user task, such as
  `character-01-generate-character`. When renaming an example, update its links
  and affected connections in the same change.
- Add units where needed, such as `duration_seconds` and `timestamp_us`.
- Never include prompts, tokens, private identifiers, or machine paths in public
  artifact names.
- Keep narrow, documented exceptions for names imposed by a framework or provider.

## Review checklist

Before accepting a new name, ask:

- Does the name describe the role or domain concept instead of the type shape?
- Is the name clear at the call site?
- Is context supplied by the owner omitted from the local name?
- Does the name avoid banned role words unless the naming policy configures an
  exception?
- Does the name use the correct language case rule?
- Does the file or directory name describe ownership?
- Does the function name start with a verb from the table, used with the
  table's meaning, and name the domain item?
- Does each boolean read as a positive assertion, unless it is a widget ID a
  person reads as a checkbox label?
- Are external names isolated to boundary modules?
- Are model, data, and result names treated as contracts?
- Does the name satisfy the configured language and structural naming checks?

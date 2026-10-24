# Bash

Read this rule when you write or change a shell script.

## Bash scope

Use Bash to run commands and wire tools together. Parsing, data structures, long-running work, and typed contracts
belong in application code.

## Deprecated and forbidden syntax

Do not use `function`, `typeset`, `&>`, `|&`, or `for arg; {`. Use `name() { ...; }`, `local`, `declare`, `readonly`,
explicit redirections, and `for arg in "$@"; do` instead. `trap ERR` does not provide general error handling. Check
failure where it matters, and reserve traps for cleanup that can run safely on the relevant exit path.

## Script structure

Open an executable script with its shebang and `set -euo pipefail`. When it defines functions, define `main` and call it
last, as `main "$@"`.

## Options

Use `errexit` as a backstop, not as control flow. It does not stop the script inside conditionals, pipelines, command
substitutions, subshells, and some functions. Check the status of `cd`, `rm`, builds, publishing, uploads, and
destructive commands explicitly. Do not toggle options around a small operation without restoring the prior state. Keep
`set -x` out of committed code.

Put explicit checks inside a function called in `if`, `while`, `&&`, or `||`, because `errexit` does not stop it there:

```bash
# cleanup: Removes the contents of the target folder.
# Arguments:
#   Target folder.
cleanup() {
    local target="$1"

    cd -- "${target}" || return 1
    find . -mindepth 1 -maxdepth 1 -exec rm -r -- {} +
}
```

Process substitution hides producer failures. When the producer status matters, write to a checked temporary file, use
`PIPESTATUS`, or call it separately. Under `pipefail`, short readers such as `head` and `grep -q` can make the producer
receive SIGPIPE and fail the pipeline. Consume input predictably or handle the known status. Under `nounset`, use
`${name:-}` where the public interface accepts an unset variable and `${name:?message}` for a required value at a clear
boundary. Use `${1:-}` where callers can omit an argument.

## Functions

Declare function-local variables with `local`. Preserve the documented status contract: a predicate may return 1 for
false, distinct from an execution error.

```bash
# report_unreadable_files: Reports each unreadable input and fails if any input is unreadable.
report_unreadable_files() {
    local path
    local status=0

    for path in "$@"; do
        if [[ -r ${path} ]]; then
            continue
        fi
        printf 'error: input is unreadable: %s\n' "${path}" >&2
        status=1
    done
    return "${status}"
}
```

### Function conventions

Use `name() { ... }` for a function that runs in the current shell, and a subshell body, `name() ( ... )`, to isolate
state and traps from the caller on purpose.

## Variables and constants

Mark constants `readonly` immediately after assignment, and `export` only what child processes need. Do not overwrite
`PATH`, `HOME`, `IFS`, `CDPATH`, `SHELL`, `PWD`, or `BASH_ENV` without a clear need. Never export `CDPATH`.

Compute a folder constant with `CDPATH='' cd -- <path> && pwd -P` and add a failure path: `|| exit 1` in an entry point
and `|| return 1` in a library. Use `$HOME`, not a quoted `~`, inside paths, and assign a home-relative value before
exporting it. Quote array elements passed to `unset -v`.

```bash
script_parent="$(dirname -- "${BASH_SOURCE[0]}")" || exit 1
PROJECT_ROOT="$(CDPATH='' cd -- "${script_parent}/.." && pwd -P)" || exit 1
readonly PROJECT_ROOT
export PROJECT_ROOT
```

## Quoting and expansion

Use single quotes for literals, double for expansions. Word splitting never parses data. Use functions, not aliases.
Parameter expansion replaces external tools for string work:

```bash
filename="archive.tar.gz"
base="${filename%.tar.gz}"
```

## Arrays and argument lists

Command arguments live in arrays, expanded with `"${array[@]}"` and never populated from raw `$(...)`. Read lines with a
`while read` loop or `readarray`, and filenames from `NUL`-delimited streams. `readarray` needs Bash 4, and macOS ships
`/bin/bash` 3.2:

```bash
declare -a archive_args
archive_args=(-czf "${archive_path}" -C "${source_directory}" .)
tar "${archive_args[@]}"

while IFS= LC_ALL=C read -r -d '' file; do
    files+=("${file}")
done < <(find . -type f -name '*.sql' -print0)
```

## Conditionals and arithmetic

`[[ ... ]]` holds string, pattern, and file tests. `-z` and `-n` test for emptiness. Numeric comparisons live in
`(( ... ))` after validation of untrusted numbers; `<` and `>` inside `[[ ... ]]` compare strings.

```bash
readonly VERSION_PATTERN='^[0-9]+\.[0-9]+\.[0-9]+$'
if [[ ${version} =~ ${VERSION_PATTERN} ]]; then
    printf 'valid version\n'
fi
```

Arithmetic uses `$(( ... ))` and `(( ... ))`. `(( i++ ))` returns false when the expression equals zero, so under
`errexit` increment with `retry_count=$(( retry_count + 1 ))`. Untrusted strings never enter `(( ... ))`, `$(( ... ))`,
`[[ value -gt n ]]`, array indices, or arithmetic `for` expressions: validate with a pattern first. `10#${value}`
converts unsigned base-10 strings.

```bash
if [[ ! ${port} =~ ^[0-9]{1,5}$ ]]; then
    printf 'error: port must be numeric\n' >&2
    return 1
fi
if ((10#${port} < 1 || 10#${port} > 65535)); then
    printf 'error: port is out of range\n' >&2
    return 1
fi
```

## Loops and delimited data

Iterate arguments with `for arg in "$@"; do`, globs directly, and files with
`while IFS= read -r line || [[ -n ${line} ]]; do ... done <"${file}"`, which keeps the last unterminated line. A pipe
into `while` runs the loop in a subshell, so variables set inside it vanish; use process substitution or a redirected
file. Counter loops use `for (( index = 0; index < count; index++ ))`, not `seq`.

```bash
root_dir="$(CDPATH='' cd -- "${1:?Root directory is required}" && pwd -P)" || exit 1
file_list="$(mktemp)" || exit 1
trap 'rm -f -- "${file_list}"' EXIT
find "${root_dir}" -type f -print0 >"${file_list}" || exit 1

while IFS= LC_ALL=C read -r -d '' file; do
    printf 'file: %q\n' "${file}"
done <"${file_list}"
```

Set `IFS` only with `local IFS` inside a function or in a subshell. Never set it for the whole script, and never save
and restore it with `old_ifs="${IFS}"`. `read` treats `IFS` as a terminator, so a controlled delimited line keeps its
trailing empty field only with an appended delimiter. Parse general CSV in application code with a real parser, never
with `IFS=, read`.

```bash
# join_path_parts: Joins the arguments with slashes.
join_path_parts() {
    local IFS='/'
    printf '%s\n' "$*"
}
```

## Paths, globs, and file names

Filenames can hold spaces, newlines, quotes, brackets, and leading dashes. Never assume the current folder; compute it,
and check `cd` explicitly. A broken symlink needs `-L` beside `-e` when existence matters, and a basename pattern reads
`"${path##*/}"`. Handle the no-match glob deliberately, either with `[[ -e ${file} ]] || continue` or with `nullglob`
scoped to a subshell:

```bash
for file in ./*.sql; do
    [[ -e ${file} ]] || continue
    printf '%s\n' "${file}"
done

if ! cd -- "${target_dir}"; then
    printf 'error: cannot enter target dir: %s\n' "${target_dir}" >&2
    return 1
fi
```

## Command substitution

Command substitution strips trailing newlines, cannot carry binary data, and never builds an argument list.

## Pipelines and redirection

Read `PIPESTATUS` immediately when individual statuses matter. Never close a standard descriptor as a shortcut for
`/dev/null`. Parallel `xargs` jobs do not produce ordered, unmixed output: write per-job files and combine them, or use
a tool that serializes. Check a command directly or capture its status in a named variable.

```bash
tar -cf - ./* | (cd -- "${target_dir}" && tar -xf -)
statuses=("${PIPESTATUS[@]}")
if ((statuses[0] != 0 || statuses[1] != 0)); then
    printf 'error: tar copy failed\n' >&2
    return 1
fi
```

## Output, logging, and errors

Write messages with `printf`, not `echo`. Return or exit with the intended status: printing an error does not make a
command fail.

End an executable script with a meaningful status. Do not let a final message, a false condition, or an optional cleanup
check set the exit status. Use an explicit `exit 0` only when the final command's status differs from the program result
and prior checks establish success.

```bash
# log_status: Prints a timestamped diagnostic line to stderr.
# Arguments:
#   Step name.
#   Target name.
#   Status label.
log_status() {
    local step_name="$1"
    local target_name="$2"
    local status_label="$3"
    local timestamp

    timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')" || return 1
    printf 'ts=%s script=%s step=%s target=%s status=%s\n' \
        "${timestamp}" "${0##*/}" "${step_name}" "${target_name}" \
        "${status_label}" >&2
}
```

## Comments and documentation

A public, sourced, complex, or risky function carries the full header with `Globals`, `Arguments`, `Outputs`, and
`Returns` sections.

## Naming

### Script and function names

- Executable scripts use `.sh` when invoked through a task runner or build rules.
- Omit the extension on an executable script only when users invoke it as a command on `PATH`.
- Give sourced libraries the `.sh` extension and no executable permission.
- Functions and mutable variables use `snake_case`.
- Use `::` in package-like function prefixes only when a script family already follows that convention.

| Avoid              | Prefer                     | Meaning              |
| ------------------ | -------------------------- | -------------------- |
| `DeployScript.sh`  | `deploy-api.sh`            | API deployment.      |
| `deploy_script.sh` | `upload-storage-assets.sh` | Storage upload.      |
| `helpers.sh`       | `archive-reports`          | A command on `PATH`. |

Name a deployment function `deploy_api` and its local target `target_environment`.

### Bash variables

- Name each loop variable after its item.
- Name a temporary path after what it holds, such as `download_file` or `work_dir`; `tmp` and `temp` say nothing.
- Avoid reserved and special shell names for unrelated values.

Use `migration_file` when iterating migration paths and `report_output` for captured report text. Check the report
command's exit status before printing the captured output. A loop variable such as `i` does not describe a file.

### Bash functions

- Give a function with side effects a verb-phrase name.
- Name a function that writes to `stdout` for the data it prints.
- Do not name scripts or functions after shell builtins or common commands.

Name a port validator `validate_port`, not `test`, which shadows a shell builtin.

## Script families

Each file owns one cohesive responsibility, and the folder supplies the family name.

- A sourced public function carries its family name, such as `release_prepare` or `cache_read_state`.
- Keep a function with one caller in the same file as the call.
- Put a related script family in its own subfolder, and give its files role names such as `main.sh`, `state.sh`,
  `query.sh`, or `report.sh`.

# Command-Line Programs

Read this rule when you change a command-line program that the project ships.

## Streams and exit status

- Data goes to stdout. Diagnostics, progress, prompts, and errors go to stderr.
- Preserve established exit codes. New commands use `0` on success, `1` on failure, and `2` on usage error unless their
  protocol defines other behavior. List each exit code in `--help`.
- Keep machine-readable `--json` output complete, stable, and free of progress text.
- Omit color and control sequences unless stdout connects to a terminal and `NO_COLOR` has no value.

## Interface

- `--help` prints usage, every flag with its default, and one example. `--version` prints the version and exits.
- Every value a prompt asks for also has a flag. If the process has no terminal, fail. Name the missing flag.
- A destructive command prompts for confirmation on a terminal and requires `--yes` otherwise.
- Help text says what the user can do, and names only commands, flags, and settings that exist. It shows no regular
  expression, internal identifier, source path of the program, or value that the user cannot change.

## Behavior

- Validate every argument before doing any work. Fail with an actionable message that names the argument.
- Make a command idempotent where the operation allows it: running it twice gives the same state.
- Long operations report progress on stderr and handle interruption: catch the termination signal, clean up, and exit
  with its status.
- Resolve a relative path against the folder the user ran the command in, or an explicit argument. Never resolve it
  against the script's own folder.
- Create temporary files with a secure call such as `mktemp` or `tempfile.mkstemp`, and delete them on exit.

## Flag naming

Use `--kebab-case` for flags. Boolean switches take no value; use `--no-flag` for negation. Preserve names defined by an
existing public interface.

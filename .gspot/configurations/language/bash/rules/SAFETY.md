# Bash Safety

Read this rule when a shell script deletes files, downloads, uses `sudo`, starts background jobs, or parses JSON or
YAML.

## Calling commands

Use fixed command names with argument arrays, never strings built from input. Never pass untrusted input to a shell.
Never use `bash -lc` in repository scripts. A function that runs a caller-supplied command takes it and its arguments
after `shift` and invokes `"$@"`.

Check uncommon commands with `command -v` before a long-running, destructive, publishing, or error-handling path depends
on them. Prefer builtins and parameter expansion to external commands for string and arithmetic work. Never run `su -c`
without the target user.

```bash
# require_command: Ensures a command exists on PATH.
# Arguments:
#   Command name.
require_command() {
    local command_name="$1"

    if ! command -v "${command_name}" >/dev/null 2>&1; then
        printf 'error: required command not found: %s\n' "${command_name}" >&2
        return 1
    fi
}
```

## Processes and privilege

Treat process names as advisory information, never authorization. Stop and restart paths kill only process ids that the
owning script family recorded, found through the service manager, a `PID` file, or `pgrep -x`, never `ps | grep`. A
script that starts background jobs saves every `PID`, waits for each job, captures its status, and writes its output to
a separate file. It bounds its fan-out and kills owned children on `INT`, `TERM`, and `EXIT`. `sudo command > file`
redirects as the current user, and a glob in `sudo command /path/*` expands before `sudo` runs. Send privileged writes
through `sudo tee`, and keep the shell string you pass to `sudo` a fixed literal with no input.

```bash
generate_config | sudo tee /etc/service/config >/dev/null

# run_remote_checks: Runs remote checks and returns non-zero on any failure.
# Globals:
#   work_dir
#   child_pids
# Arguments:
#   Small, already bounded host list to check.
run_remote_checks() {
    local host
    local pid
    local status=0

    trap 'cleanup_children' EXIT
    trap 'cleanup_children; exit 130' INT
    trap 'cleanup_children; exit 143' TERM

    for host in "$@"; do
        check_host "${host}" >"${work_dir}/${host}.log" 2>&1 &
        child_pids+=("$!")
    done

    for pid in "${child_pids[@]}"; do
        wait "${pid}" || status=1
    done

    trap - EXIT INT TERM
    return "${status}"
}
```

## Structured data

Use parameter expansion for string edits. JSON goes through `jq`, and YAML through `yq` or a project-owned parser. Never
parse JSON, YAML, XML, HTML, plist, or xcodebuild output with ad hoc `grep | sed | awk` unless the script controls the
input and the format has no complex structure. Prefer machine output modes such as JSON, `NUL`, or explicit format flags
and never parse process lists, pretty tables, progress bars, or localized text by fixed field numbers. Quote `tr`
character classes and pin `LC_ALL=C` when converting case.

```bash
# get_service_url: Prints a required nonempty service URL from JSON configuration.
get_service_url() {
    local config_file="${1:?Configuration file is required}"
    local service_url

    service_url="$(jq -er '.service.url | select(type == "string" and length > 0)' "${config_file}")" || return 1
    printf '%s\n' "${service_url}"
}
```

## Network

Download with `curl --fail --show-error --silent --location` into an explicit file. Set timeouts with the options of the
tool, such as `--connect-timeout` plus `--max-time`, or SSH `ConnectTimeout`. Do not use GNU `timeout`, which macOS
lacks.

```bash
installer="${work_dir}/install.sh"
curl --fail --show-error --silent --location \
    --connect-timeout 10 \
    --max-time 60 \
    --output "${installer}" \
    "${installer_url}" || exit 1
printf '%s  %s\n' "${expected_sha256}" "${installer}" | shasum -a 256 -c - || exit 1
bash "${installer}" --version "${tool_version}"

ssh -o ConnectTimeout=10 -o ServerAliveInterval=15 -o ServerAliveCountMax=2 \
    -- "${host}" systemctl is-active --quiet "${service_name}"
```

## Secrets and environment

An indirect expansion `${!name}` takes only a validated name.

```bash
# require_env: Ensures an environment variable is set and non-empty.
# Arguments:
#   Environment variable name.
require_env() {
    local name="$1"

    if [[ ! ${name} =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
        printf 'error: invalid env var name\n' >&2
        return 1
    fi
    if [[ -z ${!name:-} ]]; then
        printf 'error: %s is required\n' "${name}" >&2
        return 1
    fi
}
```

## Temporary files, locks, and cleanup

Create temporary paths with `mktemp` or `mktemp -d` under the system location or a dedicated project folder, never with
predictable names. Register cleanup immediately after creation. Put downloaded, copied, or generated content in a
temporary file, validate it with the real parser, and replace the destination with `mv`. The file keeps the restrictive
permissions `mktemp` gave it unless deployment needs others. Remove failed artifacts unless the script documents keeping
them. Acquire a lock atomically with `mkdir` on a folder that stores the holder `PID`, or with `noclobber` redirection,
never with a `test` followed by a create.

Stop commands remove only what the script created. Validate a cleanup path from input or persistent state against its
permitted root. Reject empty values, `/`, the repository root, `$HOME`, symlinks, and anything outside the folder the
script created.

Keep a `mktemp -d` result exactly. Never widen the path to its neighbors. Do not hide a failure with `|| true`. Handle
it, or let it stop the script.

```bash
downloaded_file="$(mktemp "${config_file}.XXXXXX")" || exit 1
trap 'rm -f -- "${downloaded_file}"' EXIT
curl --fail --show-error --silent --location --output "${downloaded_file}" "${config_url}" || exit 1
jq empty "${downloaded_file}" >/dev/null || exit 1
mv -- "${downloaded_file}" "${config_file}" || exit 1
trap - EXIT

if ! mkdir "${lock_dir}"; then
    printf 'error: lock is already held: %s\n' "${lock_dir}" >&2
    return 1
fi
printf '%s\n' "$$" >"${lock_dir}/pid" || {
    rmdir "${lock_dir}"
    return 1
}
trap 'rm -f -- "${lock_dir}/pid"; rmdir -- "${lock_dir}"' EXIT
```

Put recursive deletes in one script. To accept the `bash/safety` finding for that script, follow the suppression rules.
Validate its cleanup path against the approved root folder:

```bash
# remove_build_dir: Removes the build child of the approved root folder.
remove_build_dir() {
    local owner_root build_dir

    [[ -n $1 ]] || return 1
    owner_root="$(cd -- "$1" && pwd -P)" || return 1
    [[ ${owner_root} != / ]] || return 1
    build_dir="${owner_root}/build"
    [[ -d ${build_dir} && ! -L ${build_dir} ]] || return 1
    rm -rf -- "${build_dir}"
}
```

## Portability

macOS and BSD differ from GNU in `sed`, `date`, `readlink`, `mktemp`, `stat`, `xargs`, and `grep`; keep a
system-specific branch with the operation that owns it. Handle `realpath` and `date` parsing differences. Linux-only
utilities need checks in scripts that also run on macOS. CI does not share the `PATH` of the developer.

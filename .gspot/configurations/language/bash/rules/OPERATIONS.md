# Bash Operations

Read this rule when you write a deployment, publishing, or remote shell script.

## Deployment and publishing pipelines

Deployment, publishing, and long-running scripts separate validation, planning, confirmation, execution, readiness
checks, and cleanup.

- Fail before any work when the script lacks a required input, command, file, host, or secret.
- State the target explicitly: never infer production, a remote, a host, or an artifact from a branch name without a
  confirmation or a CI contract.
- A destructive or remote action asks for confirmation unless CI owns the guard.
- Use idempotent commands and stop at the first failed required step.
- Check readiness after deploying or publishing, and print messages a person can act on.
- Keep rollback and cleanup explicit, and delete no artifact or result as a side effect.
- Log enough to reconstruct what happened, without secrets.

```bash
# confirm_exact: Requires the user to type the expected value.
# Arguments:
#   Prompt label.
#   Expected response.
confirm_exact() {
    local label="$1"
    local expected="$2"
    local response

    printf '%s Type %s to continue: ' "${label}" "${expected}" >&2
    IFS= read -r response

    [[ ${response} == "${expected}" ]]
}
```

## Remote commands

Copy a reviewed script to the remote host and invoke it with arguments. SSH joins its arguments into one remote shell
string, so local quoting does not keep their boundaries. Validate host, user, service, and path values before you use
them. Never build a remote command from user input.

Good, for a remote Bash login shell:

```bash
printf -v remote_command 'bash -- %q %q %q' "${remote_script}" "${dir}" "${service}"
ssh -- "${host}" "${remote_command}"
```

## Persisted state

Never `source` generated state or pass it to `bash -c`. Write state in a fixed data format with an exact key schema to a
restricted file in the destination folder. A reader treats a malformed, duplicate, or unknown key as an error.

## Retries

Retry only an operation known to converge, such as a network pull or readiness polling, with a bounded number of
attempts. A retry never masks corrupt data, invalid credentials, a failed migration, a syntax error, or a permission
problem. Capture the status in the `else` branch, because an `if` whose condition fails and that has no `else` returns
zero:

```bash
if "$@"; then
    return 0
else
    status=$?
fi
```

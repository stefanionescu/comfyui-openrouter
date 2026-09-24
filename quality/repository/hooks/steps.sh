#!/usr/bin/env bash
#
# Run hook commands and report explicitly skipped checks.
# Runtime: Bash 3.2+, macOS and Linux.

# hook_run_step - Runs a hook step unless its skip variable is set.
# Globals:
#   Reads the named skip variable.
# Arguments:
#   Hook label, skip variable name, then command and arguments.
# Outputs:
#   Writes the hook status and command output.
# Returns:
#   Returns the command status, or zero when skipped.
hook_run_step() {
  local name="$1"
  local skip_var="$2"
  local skip_value="0"
  shift 2

  if [[ -n ${skip_var} ]] && [[ -n ${!skip_var+x} ]]; then
    skip_value="${!skip_var}"
  fi
  if [[ -n ${skip_var} && ${skip_value} == "1" ]]; then
    printf '[hook] skipped %s (%s=1)\n' "${name}" "${skip_var}"
    return 0
  fi

  printf '[hook] %s\n' "${name}"
  "$@"
}

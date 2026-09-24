#!/usr/bin/env bash
#
# Run Bearer security checks as a required baseline gate.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Run Bearer security checks as a required baseline gate.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  # shellcheck source=../../config/security/bearer/environment.sh
  source "${REPO_ROOT}/quality/config/security/bearer/environment.sh"

  if ! bearer scan --help >/dev/null 2>&1; then
    printf '%s\n' 'error: bearer is not available. Run: mise run repo:setup' >&2
    exit 1
  fi

  for scan_path in "${BEARER_SCAN_PATHS[@]}"; do
    bearer scan "${BEARER_FLAGS[@]}" "${scan_path}"
  done
}

main "$@"

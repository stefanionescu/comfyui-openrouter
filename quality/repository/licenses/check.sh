#!/usr/bin/env bash
#
# Check installed JavaScript dependency licenses against the package policy.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Reports license changes and packages without an approved license.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  # shellcheck source=../../config/repository/licenses/environment.sh
  source "${REPO_ROOT}/quality/config/repository/licenses/environment.sh"
  "${LICENSE_CHECKER_COMMAND[@]}" --json --out "${LICENSE_CHECKER_REPORT}"
  bun quality/repository/licenses/javascript.js "${LICENSE_CHECKER_REPORT}"
}

main "$@"

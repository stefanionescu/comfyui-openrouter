#!/usr/bin/env bash
#
# Check the frontend CodeQL configuration before scanning.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Check the frontend CodeQL configuration before scanning.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  bun quality/security/codeql/frontend/paths.js
  exec bash quality/security/codeql/frontend/scan.sh "$@"
}

main "$@"

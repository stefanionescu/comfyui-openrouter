#!/usr/bin/env bash
#
# Run Bandit security checks.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Run Bandit security checks.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  uv run --no-sync bandit -c pyproject.toml -r __init__.py src scripts quality
}

main "$@"

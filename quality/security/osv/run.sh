#!/usr/bin/env bash
#
# Audit one declared dependency lock using public OSV advisories.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Audit one declared dependency lock using public OSV advisories.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  # shellcheck source=../../config/security/osv/environment.sh
  source "${REPO_ROOT}/quality/config/security/osv/environment.sh"
  case "${1:-}" in
    python) lockfile="${OSV_PYTHON_LOCKFILE}" ;;
    frontend) lockfile="${OSV_FRONTEND_LOCKFILE}" ;;
    *)
      printf '%s\n' 'Usage: run.sh <python|frontend>' >&2
      exit 2
      ;;
  esac
  osv-scanner scan source --lockfile "${lockfile}" --config quality/config/security/osv/config.toml
}

main "$@"

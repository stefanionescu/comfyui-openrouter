#!/usr/bin/env bash
#
# Scan public sources with the repository Semgrep rules.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Scan public sources with the repository Semgrep rules.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  # shellcheck source=../../config/security/semgrep/environment.sh
  source "${REPO_ROOT}/quality/config/security/semgrep/environment.sh"
  shasum --algorithm 256 --check quality/config/security/semgrep/checksums.txt
  semgrep_arguments=(semgrep "${SEMGREP_FLAGS[@]}")
  for config_file in "${SEMGREP_LOCAL_CONFIGS[@]}"; do
    semgrep_arguments+=(--config "${config_file}")
  done
  semgrep_arguments+=("${SEMGREP_SCAN_PATHS[@]}")
  "${semgrep_arguments[@]}"
}

main "$@"

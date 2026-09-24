#!/usr/bin/env bash
#
# Scan staged content, public files, or Git history with redacted output.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Scan staged content, public files, or Git history with redacted output.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  cd "${REPO_ROOT}" || exit 1

  # shellcheck source=../../config/security/gitleaks/environment.sh
  source "${REPO_ROOT}/quality/config/security/gitleaks/environment.sh"
  uv run --no-sync python -m quality.repository.integrity.gitleaks

  gitleaks_args=("${GITLEAKS_FLAGS[@]}" --config quality/config/security/gitleaks/config.toml --baseline-path "${GITLEAKS_BASELINE_FILE}")
  case "${1:-}" in
    staged)
      gitleaks git --pre-commit --staged "${gitleaks_args[@]}" "${REPO_ROOT}"
      ;;
    worktree)
      uv run --no-sync python -m quality.security.worktree
      ;;
    history)
      gitleaks git --log-opts "${GITLEAKS_LOG_OPTS}" "${gitleaks_args[@]}" "${REPO_ROOT}"
      ;;
    "" | all)
      uv run --no-sync python -m quality.security.worktree
      gitleaks git --pre-commit --staged "${gitleaks_args[@]}" "${REPO_ROOT}"
      gitleaks git --log-opts "${GITLEAKS_LOG_OPTS}" "${gitleaks_args[@]}" "${REPO_ROOT}"
      ;;
    *)
      printf '%s\n' 'Usage: run.sh [staged|worktree|history|all]' >&2
      exit 2
      ;;
  esac
}

main "$@"

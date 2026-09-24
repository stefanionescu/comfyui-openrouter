#!/usr/bin/env bash
#
# Create and analyze the connector's JavaScript and TypeScript database.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

# main - Create and analyze the connector's JavaScript and TypeScript database.
main() {
  REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
  readonly REPO_ROOT
  cd "${REPO_ROOT}" || exit 1
  SCRIPT_DIR="${REPO_ROOT}/quality/security/codeql/frontend"
  readonly SCRIPT_DIR
  # shellcheck source=../../../config/security/codeql/frontend/environment.sh
  source "${REPO_ROOT}/quality/config/security/codeql/frontend/environment.sh"
  # shellcheck source=database.sh
  source "${SCRIPT_DIR}/database.sh"

  if (($#)); then
    printf '%s\n' 'The frontend CodeQL scan uses the repository configuration and takes no arguments.' >&2
    exit 2
  fi
  mise which codeql >/dev/null || {
    printf '%s\n' 'CodeQL is required. Run mise run repo:setup.' >&2
    exit 1
  }
  language=javascript
  threads="${CODEQL_THREADS}"
  ram_mb="${CODEQL_RAM_MB}"
  keep_database="${CODEQL_KEEP_DB}"
  if [[ ! ${threads} =~ ^[0-9]+$ || (-n ${ram_mb} && ! ${ram_mb} =~ ^[1-9][0-9]*$) || ! ${keep_database} =~ ^[01]$ ]]; then
    printf '%s\n' 'Use nonnegative CODEQL_THREADS, positive CODEQL_RAM_MB, and 0 or 1 for CODEQL_KEEP_DB.' >&2
    exit 2
  fi
  query_suites=("${CODEQL_JAVASCRIPT_QUERY_SUITES[@]}")
  source_root_abs="${REPO_ROOT}"
  config_file_abs="${REPO_ROOT}/quality/config/security/codeql/frontend/scan.yml"
  artifact_root=''
  database_dir=''
  sarif_file=''
  codeql_configure_paths "${source_root_abs}" "${config_file_abs}"
  trap codeql_cleanup_database EXIT
  codeql_create_arguments "${source_root_abs}" "${config_file_abs}"
  codeql_analyze_arguments
  codeql_run_commands
  bun "${SCRIPT_DIR}/sarif.js" "${sarif_file}"
  printf '%s\n' 'CodeQL frontend scan passed.'
}

main "$@"

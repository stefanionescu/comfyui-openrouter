#!/usr/bin/env bash
#
# Create and analyze a Python CodeQL database.
# Runtime: Bash 3.2+, macOS and Linux.
set -euo pipefail

REPO_ROOT="${MISE_PROJECT_ROOT:-$(git rev-parse --show-toplevel)}"
readonly REPO_ROOT
cd "${REPO_ROOT}" || exit 1

# shellcheck source=../../../config/security/codeql/python/environment.sh
source "${REPO_ROOT}/quality/config/security/codeql/python/environment.sh"
# shellcheck source=../../../config/security/codeql/python/scan.sh
source "${REPO_ROOT}/quality/config/security/codeql/python/scan.sh"

# shellcheck source=../cleanup.sh
source "${REPO_ROOT}/quality/security/codeql/cleanup.sh"

# _configure_codeql_python - Pins extraction to mise's project Python.
_configure_codeql_python() {
  local mise_python
  local mise_python_dir
  local resolved_python

  if ! mise_python="$(mise which "${CODEQL_PYTHON_EXECUTABLE_NAME}")"; then
    printf 'CodeQL requires the mise-managed project Python.\n' >&2
    return 1
  fi
  if [[ ! -x ${mise_python} ]]; then
    printf 'CodeQL Python is not executable: %s\n' "${mise_python}" >&2
    return 1
  fi

  mise_python_dir="${mise_python%/*}"
  PATH="${mise_python_dir}:${PATH}"
  export PATH
  if ! resolved_python="$(command -v "${CODEQL_PYTHON_EXECUTABLE_NAME}")"; then
    printf 'CodeQL could not resolve %s.\n' "${CODEQL_PYTHON_EXECUTABLE_NAME}" >&2
    return 1
  fi
  if [[ ${resolved_python} == "${REPO_ROOT}/.venv/"* ]]; then
    printf 'CodeQL refuses repository-venv interpreter: %s\n' "${resolved_python}" >&2
    return 1
  fi
  if [[ ${resolved_python%/*} != "${mise_python_dir}" ]]; then
    printf 'CodeQL resolved Python outside the mise installation: %s\n' "${resolved_python}" >&2
    return 1
  fi
}

# _cleanup_python_database - Removes only the database created by this scan.
# Globals:
#   Reads CODEQL_KEEP_DB, CODEQL_ARTIFACT_ROOT, CODEQL_DATABASE_DIR, REPO_ROOT, and database_dir.
# Arguments:
#   None.
# Outputs:
#   Removes only the database created by this invocation.
# Returns:
#   Zero when retained or removed; nonzero for invalid ownership or removal failure.
_cleanup_python_database() {
  [[ ${CODEQL_KEEP_DB} == '1' ]] && return 0
  [[ ${database_dir} == "${REPO_ROOT}/${CODEQL_ARTIFACT_ROOT}/${CODEQL_DATABASE_DIR}."* ]] || return 1
  runtime_remove_owned_path "${REPO_ROOT}" "${database_dir}"
}

# main - Creates and analyzes the repository Python CodeQL database.
main() {
  _configure_codeql_python

  export LGTM_PYTHON_SETUP_VERSION="${CODEQL_PYTHON_MAJOR_VERSION}"
  export CODEQL_EXTRACTOR_PYTHON_ANALYSIS_VERSION="${CODEQL_PYTHON_ANALYSIS_VERSION}"
  export CODEQL_EXTRACTOR_PYTHON_OPTION_PYTHON_EXECUTABLE_NAME="${CODEQL_PYTHON_EXECUTABLE_NAME}"

  if [[ ! ${CODEQL_KEEP_DB} =~ ^[01]$ ]]; then
    printf '%s\n' 'Use 0 or 1 for CODEQL_KEEP_DB.' >&2
    return 2
  fi
  for artifact_parent in .artifacts .artifacts/security .artifacts/security/codeql .artifacts/security/codeql/python; do
    if [[ -L "${REPO_ROOT}/${artifact_parent}" ]]; then
      printf '%s\n' 'CodeQL artifact directories must not be symbolic links.' >&2
      return 1
    fi
  done
  mkdir -p "${CODEQL_ARTIFACT_ROOT}"
  database_dir="$(mktemp -d "${REPO_ROOT}/${CODEQL_ARTIFACT_ROOT}/${CODEQL_DATABASE_DIR}.XXXXXX")"
  trap _cleanup_python_database EXIT
  mise exec -- codeql database create \
    --language="${CODEQL_LANGUAGE}" \
    --source-root="${REPO_ROOT}" \
    --codescanning-config="${CODEQL_CONFIG_FILE}" \
    --build-mode=none \
    --overwrite \
    "${database_dir}"
  mise exec -- codeql database analyze \
    --format="${CODEQL_SARIF_FORMAT}" \
    --output="${CODEQL_ARTIFACT_ROOT}/${CODEQL_SARIF_FILE}" \
    --download \
    "${database_dir}" \
    "${CODEQL_QUERY_SUITES[@]}"
  uv run --no-sync python -m quality.security.codeql.python.sarif \
    "${CODEQL_ARTIFACT_ROOT}/${CODEQL_SARIF_FILE}"
}

main "$@"

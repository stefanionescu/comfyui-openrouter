#!/usr/bin/env bash
#
# Configure and run CodeQL database scans.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck disable=SC2154
# lint:justify -- reason: scan.sh supplies these values before sourcing and calling this file.
# shellcheck source=../cleanup.sh
source "${REPO_ROOT}/quality/security/codeql/cleanup.sh"

# codeql_configure_paths - Validates scan paths and prepares artifact paths.
# Globals:
#   Reads repository and CodeQL settings; sets artifact_root, database_dir, and sarif_file.
# Arguments:
#   Source root and scan configuration path.
# Outputs:
#   Creates the owned database directory; writes failures to standard error.
# Returns:
#   Zero when paths are ready; nonzero on invalid paths or filesystem failure.
codeql_configure_paths() {
  local source_root_abs="$1"
  local config_file_abs="$2"

  [[ -d ${source_root_abs} ]] || {
    printf 'error: source root not found: %s\n' "${source_root_abs}" >&2
    return 1
  }
  if [[ ! -f ${config_file_abs} ]]; then
    printf 'error: missing %s\n' "${config_file_abs}" >&2
    return 1
  fi

  artifact_root="${REPO_ROOT}/${CODEQL_ARTIFACT_ROOT}"
  sarif_file="${artifact_root}/${language}${CODEQL_SARIF_EXTENSION}"
  for artifact_parent in .artifacts .artifacts/security .artifacts/security/codeql .artifacts/security/codeql/frontend; do
    if [[ -L "${REPO_ROOT}/${artifact_parent}" ]]; then
      printf '%s\n' 'CodeQL artifact directories must not be symbolic links.' >&2
      return 1
    fi
  done
  mkdir -p -- "${artifact_root}"
  database_dir="$(mktemp -d "${artifact_root}/${CODEQL_DATABASE_DIR_PREFIX}${language}.XXXXXX")"
}

# codeql_cleanup_database - Removes the database unless retention is enabled.
# Globals:
#   Reads keep_database, database_dir, artifact_root, and language.
# Arguments:
#   None.
# Outputs:
#   Removes the owned database unless retention is enabled.
# Returns:
#   Zero when retained or removed; nonzero for invalid ownership or removal failure.
codeql_cleanup_database() {
  [[ ${keep_database} == '1' ]] && return 0
  [[ ${database_dir} == "${artifact_root}/${CODEQL_DATABASE_DIR_PREFIX}${language}."* ]] || return 1
  runtime_remove_owned_path "${REPO_ROOT}" "${database_dir}"
}

# codeql_create_arguments - Builds database creation command arguments.
# Globals:
#   Reads CodeQL settings and database_dir; writes create_args.
# Arguments:
#   Source root and scan configuration path.
# Outputs:
#   None.
# Returns:
#   Zero.
codeql_create_arguments() {
  local source_root_abs="$1"
  local config_file_abs="$2"

  create_args=(
    mise exec -- codeql
    database
    create
    "--language=${language}"
    "--source-root=${source_root_abs}"
    "--codescanning-config=${config_file_abs}"
    "--threads=${threads}"
    --overwrite
  )
  if [[ -n ${ram_mb} ]]; then
    create_args+=("--ram=${ram_mb}")
  fi
  create_args+=(--build-mode=none)
  create_args+=(-- "${database_dir}")
}

# codeql_analyze_arguments - Builds database analysis command arguments.
# Globals:
#   Reads CodeQL settings and query_suites; writes analyze_args.
# Arguments:
#   None.
# Outputs:
#   None.
# Returns:
#   Zero.
codeql_analyze_arguments() {
  analyze_args=(
    mise exec -- codeql
    database
    analyze
    "--format=${CODEQL_SARIF_FORMAT}"
    "--output=${sarif_file}"
    "--threads=${threads}"
    --no-print-diagnostics-summary
    --download
  )
  if [[ -n ${ram_mb} ]]; then
    analyze_args+=("--ram=${ram_mb}")
  fi
  analyze_args+=(-- "${database_dir}" "${query_suites[@]}")
}

# codeql_run_commands - Creates and analyzes the CodeQL database.
# Globals:
#   Reads language, create_args, and analyze_args.
# Arguments:
#   None.
# Outputs:
#   Writes CodeQL progress and findings.
# Returns:
#   Returns the CodeQL command status.
codeql_run_commands() {
  printf 'CodeQL %s scan running.\n' "${language}" >&2
  "${create_args[@]}"
  "${analyze_args[@]}"
}

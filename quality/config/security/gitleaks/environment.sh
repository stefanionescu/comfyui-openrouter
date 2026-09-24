#!/usr/bin/env bash
#
# Define gitleaks configuration values.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: Gitleaks policy is sourced by scanner scripts -- ticket: quality-security
# shellcheck disable=SC2034
[[ -n ${_CFG_GITLEAKS_READY:-} ]] && return 0
readonly _CFG_GITLEAKS_READY=1

GITLEAKS_BASELINE_FILE="quality/config/security/gitleaks/baseline.json"
GITLEAKS_REASON_FILE="quality/config/security/gitleaks/reasons.json"
GITLEAKS_FLAGS=(
  --no-banner
  --redact
  --ignore-gitleaks-allow
)
GITLEAKS_LOG_OPTS="--all"
readonly GITLEAKS_BASELINE_FILE
readonly GITLEAKS_REASON_FILE
readonly GITLEAKS_LOG_OPTS
readonly -a GITLEAKS_FLAGS

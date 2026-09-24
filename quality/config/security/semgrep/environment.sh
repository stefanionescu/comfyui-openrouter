#!/usr/bin/env bash
#
# Define semgrep configuration values.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: Semgrep policy is sourced by the scanner entrypoint -- ticket: quality-security
# shellcheck disable=SC2034
[[ -n ${_CFG_SEMGREP_READY:-} ]] && return 0
readonly _CFG_SEMGREP_READY=1

SEMGREP_FLAGS=(
  --error
  --no-rewrite-rule-ids
  --metrics=off
  --disable-version-check
  --exclude=.artifacts/security/semgrep/rules
)
SEMGREP_LOCAL_CONFIGS=(
  .artifacts/security/semgrep/rules/python.json
  .artifacts/security/semgrep/rules/bandit.json
  .artifacts/security/semgrep/rules/owasp-top-ten.json
  .artifacts/security/semgrep/rules/secrets.json
  .artifacts/security/semgrep/rules/bash.json
  quality/config/security/semgrep/python.yml
  quality/config/security/semgrep/secrets.yml
  quality/config/security/semgrep/markers.yml
  quality/config/security/semgrep/frontend.yml
  quality/config/security/semgrep/hooks.yml
)
SEMGREP_SCAN_PATHS=(__init__.py src scripts quality web .githooks .mise)
readonly -a SEMGREP_FLAGS
readonly -a SEMGREP_LOCAL_CONFIGS
readonly -a SEMGREP_SCAN_PATHS

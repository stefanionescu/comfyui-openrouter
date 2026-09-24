#!/usr/bin/env bash
#
# Define bearer configuration values.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: Bearer policy is sourced by scanner scripts -- ticket: quality-security
# shellcheck disable=SC2034
[[ -n ${_CFG_BEARER_READY:-} ]] && return 0
readonly _CFG_BEARER_READY=1

BEARER_SCAN_PATHS=(__init__.py src scripts quality web/scripts)
BEARER_FLAGS=(
  --ignore-file "quality/config/security/bearer/false-positives.json"
  --severity "critical,high,medium"
  --format json
  --quiet
  --no-extract
  --disable-version-check
  --exit-code 1
)
readonly -a BEARER_SCAN_PATHS
readonly -a BEARER_FLAGS

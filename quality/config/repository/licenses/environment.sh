#!/usr/bin/env bash
#
# Define licenses configuration values.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: root package policy is sourced by license scripts -- ticket: quality-config
# shellcheck disable=SC2034
[[ -n ${_CFG_LICENSES_READY:-} ]] && return 0
readonly _CFG_LICENSES_READY=1

LICENSE_CHECKER_REPORT='.artifacts/security/licenses/frontend.json'
LICENSE_CHECKER_COMMAND=(bun --bun node_modules/license-checker/bin/license-checker)
readonly LICENSE_CHECKER_REPORT
readonly -a LICENSE_CHECKER_COMMAND

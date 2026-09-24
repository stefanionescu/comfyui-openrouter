#!/usr/bin/env bash
#
# Define osv configuration values.
# Runtime: Bash 3.2+, macOS and Linux.
# shellcheck shell=bash
# lint:justify -- reason: scanner scripts consume these lockfile paths.
# shellcheck disable=SC2034
[[ -n ${_CFG_OSV_READY:-} ]] && return 0
readonly _CFG_OSV_READY=1

OSV_PYTHON_LOCKFILE="uv.lock"
OSV_FRONTEND_LOCKFILE="bun.lock"
readonly OSV_PYTHON_LOCKFILE OSV_FRONTEND_LOCKFILE

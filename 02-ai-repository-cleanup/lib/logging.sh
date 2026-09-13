#!/usr/bin/env bash
# lib/logging.sh – Per-repository logging
# --------------------------------------------------------------
# Usage: source this file, then call write_log
# Requires: lib/env.sh to be sourced first

set -euo pipefail

mkdir -p "${BASE_DIR}/logs"

write_log() {
  local repo="$1"
  local branch="$2"
  local commit="$3"
  local stack="$4"
  local status="$5"
  local log_file="${BASE_DIR}/logs/${repo}.txt"

  {
    echo "=== START LOG ${repo} ==="
    echo "Branch: ${branch}"
    echo "Commit: ${commit}"
    echo "Stack: ${stack}"
    echo "Status: ${status}"
    echo "=== END LOG ${repo} ==="
  } > "${log_file}"
  echo "📝 Log written → $(basename "${log_file}")"
}
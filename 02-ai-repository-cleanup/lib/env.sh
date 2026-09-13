#!/usr/bin/env bash
# lib/env.sh – Load environment configuration
# --------------------------------------------------------------
# Usage: source this file
# Exposes: BASE_DIR, GITHUB_ORG, GITLAB_GROUP, REPO_LIMIT, AI_CLI_ORDER

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="${SCRIPT_DIR}/../.env"

if [[ -f "$ENV_PATH" ]]; then
  source "$ENV_PATH"
fi

: "${BASE_DIR:=/mnt/HDD1/repository-cleanup-dir}"
: "${GITHUB_ORG:=Aldo-f}"
: "${GITLAB_GROUP:=Aldo-f}"
: "${REPO_LIMIT:=100}"
: "${AI_CLI_ORDER:=hermes,opencode,claude}"
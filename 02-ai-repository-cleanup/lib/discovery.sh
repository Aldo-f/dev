#!/usr/bin/env bash
# lib/discovery.sh – Repository discovery for GitHub and GitLab
# --------------------------------------------------------------
# Usage: source this file, then call discover_repos
# Output: writes ${BASE_DIR}/repos.tsv (tab-separated:platform:repo_name:ssh_url)
# Requires: lib/env.sh to be sourced first

set -euo pipefail

discover_repos() {
  local output_file="${BASE_DIR}/repos.tsv"
  {
    gh repo list "${GITHUB_ORG}" --limit "${REPO_LIMIT}" --json name,sshUrl,visibility \
      | jq -r '.[] | [\"github\", .name, .sshUrl] | @tsv'
    glab repo list -u "${GITLAB_GROUP}" -P "${REPO_LIMIT}" -F json \
      | jq -r '.[] | [\"gitlab\", .name, .ssh_url_to_repo] | @tsv' 2>/dev/null || true
  } > "${output_file}"

  local count
  count=$(wc -l < "${output_file}")
  echo "📦 ${count} repositories discovered."
}
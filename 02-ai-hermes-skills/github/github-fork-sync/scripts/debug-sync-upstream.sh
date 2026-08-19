#!/usr/bin/env bash
# Debug script for sync-upstream workflow failures
# Usage: ./scripts/debug-sync-upstream.sh <RUN_ID>

set -euo pipefail

RUN_ID="${1:-}"
if [ -z "$RUN_ID" ]; then
  echo "Usage: $0 <RUN_ID>"
  echo "  RUN_ID: GitHub Actions run ID (from 'gh run list')"
  exit 1
fi

REPO="Aldo-f/hermes-webui"
WORKFLOW="sync-upstream.yml"

echo "=== Debugging sync-upstream run $RUN_ID ==="
echo

echo "1. Run overview:"
gh run view "$RUN_ID" --repo "$REPO" --json conclusion,createdAt,headBranch,headSha,displayTitle,workflowName,jobs

echo
echo "2. Failed job logs:"
gh run view "$RUN_ID" --repo "$REPO" --log-failed 2>/dev/null || echo "  (no failed steps or --log-failed not available)"

echo
echo "3. Full log (last 100 lines):"
gh run view "$RUN_ID" --repo "$REPO" --log | tail -100

echo
echo "4. Workflow file content (from repo):"
gh api repos/"$REPO"/contents/.github/workflows/"$WORKFLOW" --jq '.content' | base64 -d

echo
echo "=== Common failure patterns to check ==="
echo "  - '--exit-data' typo (should be '--exit-code')"
echo "  - Missing 'workflows: write' permission when upstream modifies workflow files"
echo "  - Missing git config user.name/user.email"
echo "  - Push rejected due to permissions"
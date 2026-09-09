#!/usr/bin/env bash
# --------------------------------------------------------------
# cleanup-test.sh – test mode: process only first N repos non-interactively
# --------------------------------------------------------------
set -euo pipefail

source ~/.hermes/cleanup.env 2>/dev/null || true
: "${BASE_DIR:=\${HOME}/dev}"
: "${GITHUB_ORG:=Aldo-f}"
: "${GITLAB_GROUP:=Aldo-f}"
: "${REPO_LIMIT:=100}"
: "${TEST_MODE:=1}"  # skip interactive prompts

echo "🧪 TEST MODE: Processing first $REPO_LIMIT repos (non-interactive)"
echo ""

# Generate repos list
mkdir -p "${BASE_DIR}/logs"
{
  gh repo list "$GITHUB_ORG" --limit "$REPO_LIMIT" --json name,sshUrl,visibility \
    | jq -r '.[] | ["github", .name, .sshUrl] | @tsv'
  glab repo list "$GITLAB_GROUP" -P "$REPO_LIMIT" --json name,sshUrl,visibility \
    | jq -r '.[] | ["gitlab", .name, .sshUrl] | @tsv' 2>/dev/null || true
} > "${BASE_DIR}/repos.tsv"

total=$(wc -l < "${BASE_DIR}/repos.tsv")
echo "📦 Found $total repositories"
echo ""

# Process first 3 repos as demo
count=0
while IFS=$'\t' read -r platform repo_name repo_ssh; do
  count=$((count + 1))
  if [[ $count -gt 3 ]]; then
    break
  fi
  
  echo "=== [$platform] $repo_name ==="
  
  target_dir="${BASE_DIR}/${platform}s/${repo_name}"
  mkdir -p "$(dirname "$target_dir")"
  
  if [[ -d "$target_dir/.git" ]]; then
    echo "📂 Reusing existing clone"
    cd "$target_dir"
  else
    echo "📥 Cloning..."
    git clone --depth 1 "$repo_ssh" "$target_dir"
    cd "$target_dir"
  fi
  
  # Detect stack
  stack="unknown"
  [[ -f package.json ]] && stack="node"
  [[ -f requirements.txt ]] && stack="python"
  [[ -f go.mod ]] && stack="go"
  echo "🔍 Stack: $stack"
  
  # Run basic cleanup (no lint/format for speed)
  echo "🧹 Running cleanup..."
  cleanup_branch="cleanup/test-${repo_name}"
  git checkout -b "$cleanup_branch" 2>/dev/null || git checkout "$cleanup_branch" 2>/dev/null || true
  
  # Create .env.example if missing
  [[ -f .env.example ]] || echo "# Environment variables example" > .env.example
  [[ -f SECURITY.md ]] || echo "# SECURITY\nUse env vars for secrets." > SECURITY.md
  
  # Update .gitignore
  cat >> .gitignore <<'EOF'
.env
.env.*
node_modules/
__pycache__/
*.log
EOF
  
  git add .
  git commit -m "test: cleanup for $repo_name" 2>/dev/null || echo "⚠️  No changes to commit"
  
  # Write log
  log_file="${BASE_DIR}/logs/${repo_name}.txt"
  {
    echo "=== START LOG ${repo_name} ==="
    echo "Platform: $platform"
    echo "Branch: $cleanup_branch"
    echo "Stack: $stack"
    echo "Status: test-complete"
    echo "=== END LOG ${repo_name} ==="
  } > "$log_file"
  echo "📝 Log: $(basename "$log_file")"
  
  echo "✅ Done"
  cd "$BASE_DIR"
  echo ""
done < "${BASE_DIR}/repos.tsv"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Test complete – processed $count repos"
echo "📁 Logs: ${BASE_DIR}/logs/"
echo ""
echo "To run full cleanup:"
echo "   hermes chat --session cleanup-session  # (optional, for AI hints)"
echo "   bash cleanup-master.sh"

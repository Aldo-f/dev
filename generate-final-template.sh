#!/usr/bin/env bash
# --------------------------------------------------------------
# generate-final-template.sh – create reusable cleanup template
# from collected AI hints
# --------------------------------------------------------------
set -euo pipefail

BASE_DIR="${HOME}/dev"
AI_HINTS="${BASE_DIR}/ai-hints.json"
TEMPLATE="${BASE_DIR}/cleanup-template.sh"

# Check if ai-hints.json exists and has content
if [[ ! -f "$AI_HINTS" ]] || [[ "$(jq 'keys|length' "$AI_HINTS")" -eq 0 ]]; then
  echo "⚠️  No AI hints found at $AI_HINTS"
  echo "   Run cleanup-master.sh first to collect suggestions."
  exit 0
fi

# Create the template file header
cat > "$TEMPLATE" <<'EOF'
#!/usr/bin/env bash
# --------------------------------------------------------------
# cleanup-template.sh – reusable cleanup script with AI patches
# --------------------------------------------------------------
set -euo pipefail

BASE_DIR="/mnt/HDD1/dev"

EOF

# Append all code_change snippets in order of appearance
echo "# <<< AI PATCH START >>>" >> "$TEMPLATE"
jq -r 'to_entries[] | .value.code_change // empty' "$AI_HINTS" >> "$TEMPLATE"
echo "# <<< AI PATCH END >>>" >> "$TEMPLATE"

# Append the generic cleanup logic (from cleanup-master.sh)
cat >> "$TEMPLATE" <<'EOF'

# Generic cleanup function
cleanup_repo() {
  local path="$1"
  echo "🚀 Cleaning $path"
  cd "$path"

  # Detect stack
  local stack="unknown"
  if [[ -f package.json ]]; then
    stack="node"
  elif [[ -f requirements.txt ]]; then
    stack="python"
  elif [[ -f go.mod ]]; then
    stack="go"
  elif [[ -f pom.xml ]]; then
    stack="java-maven"
  fi

  # Secret scan (if available)
  command -v trufflehog >/dev/null && trufflehog filesystem . > "${path}_secrets.txt" || true

  # Lint / format per stack
  case "$stack" in
    node)  npm ci && npm run lint || true; npx prettier --write . ;;
    python) pip install -r requirements.txt --quiet || true; command -v black >/dev/null && black . ;;
    go)    go mod tidy; go fmt ./... ;;
    java-maven) mvn spotless:apply || true ;;
  esac

  # Add missing files if needed
  [[ -f .env.example ]] || cp /usr/local/share/templates/.env.example .
  [[ -f SECURITY.md ]] || cat > SECURITY.md <<SEC
# SECURITY
## Secrets
Never commit real secrets. All secrets must be provided via environment variables (see .env.example).
SEC

  # Append generic ignore rules
  cat >> .gitignore <<IGNORE

# Auto‑generated ignore rules
.env
.env.*
node_modules/
.venv/
__pycache__/
.go/
target/
*.log
*.bak
*_test.*
IGNORE

  # Commit and push a dedicated cleanup branch
  local branch="cleanup/$(date +%Y%m%d)-$(basename "$path")"
  git checkout -b "$branch"
  git add .
  git commit -m "chore: automated cleanup – generic pipeline"
  git push -u origin "$branch"
}

# ------------------------------------------------------------------
# MAIN – iterate over repositories listed in repos.tsv
# ------------------------------------------------------------------
while IFS=$'\t' read -r platform repo_name repo_ssh; do
  target="${BASE_DIR}/${platform}s/${repo_name}"
  [[ -d "$target/.git" ]] || git clone "$repo_ssh" "$target"
  cleanup_repo "$target"
done < "${BASE_DIR}/repos.tsv"
EOF

chmod +x "$TEMPLATE"
hints_count=$(jq 'keys|length' "$AI_HINTS")
echo "✅ Generated $TEMPLATE with $hints_count AI patches."
echo "   You can now share this script with others."

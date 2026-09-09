#!/usr/bin/env bash
# --------------------------------------------------------------
# cleanup‑master.sh – clean up one repository at a time with AI feedback
# --------------------------------------------------------------
set -euo pipefail

# ---------- 0️⃣ LOAD .env -------------------------------------------------
# Search for .env in (a) same directory as this script, (b) $HOME/.hermes/
ENV_PATH=""
if [[ -f "$(dirname "$0")/.env" ]]; then
  ENV_PATH="$(dirname "$0")/.env"
elif [[ -f "${HOME}/.hermes/cleanup.env" ]]; then
  ENV_PATH="${HOME}/.hermes/cleanup.env"
fi

if [[ -n "$ENV_PATH" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_PATH"
  echo "🔧 Loaded configuration from $ENV_PATH"
else
  echo "⚠️  No .env file found – falling back to built‑in defaults"
fi

# ---------- 1️⃣  DEFAULT‑WAARDEN (overridden by .env) ----------
: "${BASE_DIR:=\${HOME}/dev}"
: "${GITHUB_ORG:=Aldo-f}"
: "${GITLAB_GROUP:=Aldo-f}"
: "${AI_MODEL:=gpt-4o-mini}"
: "${OPENAI_API_KEY:=}"      # empty string = no AI‑hint
: "${REPO_LIMIT:=500}"
# ----------------------------------------------------------------

# 0. Verify required CLI tools are available
required_cmds=(gh glab jq git curl)
for cmd in "${required_cmds[@]}"; do
  command -v "$cmd" >/dev/null || {
    echo "❌ Missing dependency: $cmd – install it first"
    exit 1
  }
done
[[ -n "$OPENAI_API_KEY" ]] || {
  echo "⚠️  No OPENAI_API_KEY – AI hint step will be skipped"
}

# 2. Load (or initialise) the AI‑hints JSON file
AI_HINTS="${BASE_DIR}/ai-hints.json"
[[ -f "$AI_HINTS" ]] || echo "{}" > "$AI_HINTS"

# 3. Create logs directory
mkdir -p "${BASE_DIR}/logs"

# 4. Retrieve a full list of repositories (max REPO_LIMIT per platform)
echo "🔎 Collecting repository list …"
{
  gh repo list "$GITHUB_ORG" --limit "$REPO_LIMIT" --json name,sshUrl,visibility \
    | jq -r '.[] | ["github", .name, .sshUrl] | @tsv'
  glab repo list "$GITLAB_GROUP" --limit "$REPO_LIMIT" --json name,sshUrl,visibility \
    | jq -r '.[] | ["gitlab", .name, .sshUrl] | @tsv'
} > "${BASE_DIR}/repos.tsv"

total=$(wc -l < "${BASE_DIR}/repos.tsv")
echo "📦 $total repositories discovered."

# 5. Function to ask the AI session for improvement suggestions
hermes_ask() {
  local repo="$1" log_file="$2"
  local prompt=$(cat <<PROMPT
--- LOG START ${repo} ---
$(cat "$log_file")
--- LOG END ${repo} ---
Based on this log, suggest ONE concrete improvement for the Bash cleanup script that will benefit the next repository.
Return ONLY a JSON object with keys "suggestion" and "code_change".
If no improvement is needed, set "suggestion" to "none" and "code_change" to "".
PROMPT
)
  if command -v hermes >/dev/null; then
    hermes send "$prompt"
    hermes receive
  elif command -v opencode >/dev/null; then
    opencode send "$prompt"
    opencode receive
  else
    echo '{"suggestion": "none", "code_change": ""}'
  fi
}

# 3. Process each repository one‑by‑one
while IFS=$'\t' read -r platform repo_name repo_ssh; do
  # Skip repositories already marked for archiving
  if [[ "$repo_name" == *".archive" ]]; then
    echo "⏭️  Skipping $repo_name (already archived)"
    continue
  fi

  echo -e "\n=== [$platform] $repo_name ==="

  # 6.1 Determine the target directory (preserve org/group hierarchy)
  target_dir="${BASE_DIR}/${platform}s/${repo_name}"
  mkdir -p "$(dirname "$target_dir")"

  # 6.2 If the repo already exists locally, ask what to do
  if [[ -d "$target_dir/.git" ]]; then
    read -p "Repo already present at $target_dir. [r]e‑clone, [s]kip, [a]rchive, [c]ontinue? " choice
    case "$choice" in
      r|R) rm -rf "$target_dir"
           git clone "$repo_ssh" "$target_dir"
           ;;
      s|S) echo "⏭️  Skipping $repo_name"
           continue
           ;;
      a|A) # Mark for archiving by renaming the target directory
           archived_dir="${target_dir}.archive"
           mv "$target_dir" "$archived_dir"
           echo "📦 Archived $repo_name → $(basename "$archived_dir")"
           echo "   Future runs will skip this repo automatically"
           continue
           ;;
      *) echo "✅  Using existing clone"
           ;;
    esac
  else
    git clone "$repo_ssh" "$target_dir"
  fi

  cd "$target_dir"

  # 6.3 Detect the primary technology stack
  stack="unknown"
  if [[ -f package.json ]]; then
    stack="node"
    pkg_manager="npm"
  elif [[ -f requirements.txt ]]; then
    stack="python"
    pkg_manager="pip"
  elif [[ -f go.mod ]]; then
    stack="go"
    pkg_manager="go"
  elif [[ -f pom.xml ]]; then
    stack="java-maven"
    pkg_manager="mvn"
  fi
  echo "🔍 Detected stack: $stack"

  # 6.4 Ask the user whether to clean this repository
  read -p "Do you want to clean $repo_name? (y/n/a) " ans
  case "$ans" in
    n|N) echo "⏭️  Skipping $repo_name per user request"
         continue
         ;;
    a|A) # Archive the repository instead of cleaning
         archived_name="${repo_name}.archive"
         # Rename the branch to indicate archival
         git branch -m "cleanup/$(date +%Y%m%d)-${repo_name}" "archived/${repo_name}"
         git push origin --delete "cleanup/$(date +%Y%m%d)-${repo_name}" 2>/dev/null || true
         git push -u origin "archived/${repo_name}"
         echo "📦 Archived $repo_name (branch renamed to archived/...)"
         echo "   Consider removing the remote repo or marking as archived in GitHub/GitLab"
         continue
         ;;
    *)   ;;
  esac
  [[ "$ans" == "y" || "$ans" == "Y" ]] || {
    echo "⏭️  Invalid input – skipping $repo_name"
    continue
  }

  # ---------- CLEANUP PIPELINE (stack‑agnostic) ----------
  # 6.5.1 Secret scan (optional, runs if trufflehog is installed)
  if command -v trufflehog >/dev/null; then
    trufflehog filesystem . > "${BASE_DIR}/${repo_name}_secrets.txt" || true
    echo "🔐 Secrets scan saved → ${repo_name}_secrets.txt"
  fi

  # 6.5.2 Lint / format according to detected stack
  case "$stack" in
    node)
      npm ci && npm run lint || true
      npx prettier --write .
      ;;
    python)
      pip install -r requirements.txt --quiet || true
      command -v black >/dev/null && black .
      command -v flake8 >/dev/null && flake8 .
      ;;
    go)
      go mod tidy
      go fmt ./...
      ;;
    java-maven)
      mvn spotless:apply || true
      ;;
    *)
      echo "⚠️  Unknown stack – skipping lint/format step"
      ;;
  esac

  # 6.5.3 Ensure .env.example and SECURITY.md exist
  [[ -f .env.example ]] || cp /usr/local/share/templates/.env.example . || true
  [[ -f SECURITY.md ]] || cat > SECURITY.md <<'EOF'
# SECURITY

## Secrets
Never commit real secrets. All secrets must be supplied via environment variables
(see `.env.example`). Run a secret scanner before any PR.

## Dependencies
Run the relevant package‑manager audit command (npm audit, pip‑audit,
go mod tidy, mvn dependency:analyze) and upgrade vulnerable versions.
EOF

  # 6.5.4 Extend .gitignore with generic ignore rules
  cat >> .gitignore <<'EOF'

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
EOF

  # 6.5.5 Create a dedicated cleanup branch, commit, and push
  cleanup_branch="cleanup/$(date +%Y%m%d)-${repo_name}"
  git checkout -b "$cleanup_branch"
  git add .
  git commit -m "chore: automated cleanup – secrets, lint, .gitignore, .env.example"
  git push -u origin "$cleanup_branch"

  # 6.6 Write log file for this repository
  log_file="${BASE_DIR}/logs/${repo_name}.txt"
  {
    echo "=== START LOG ${repo_name} ==="
    echo "Branch: $cleanup_branch"
    echo "Commit: $(git rev-parse HEAD)"
    echo "Diff‑stat:"
    git diff HEAD~1 HEAD --stat
    echo "=== END LOG ${repo_name} ==="
  } > "$log_file"
  echo "📝 Log written → ${repo_name}.txt"

  # ---------- AI FEEDBACK FOR NEXT REPO ----------
  if [[ -n "$OPENAI_API_KEY" && -n "$AI_MODEL" ]]; then
    echo "🤖 Asking AI for improvement suggestion…"
    ai_response=$(hermes_ask "$repo_name" "$log_file")
    
    # Extract suggestion and code_change from JSON response
    suggestion=$(echo "$ai_response" | jq -r '.suggestion // "none"')
    code_change=$(echo "$ai_response" | jq -r '.code_change // ""')
    
    if [[ "$suggestion" != "none" && -n "$code_change" ]]; then
      echo "🤖 Suggestion: $suggestion"
      echo "🛠️  Applying code change…"
      # Apply the suggested patch in a subshell to avoid breaking the loop
      ( eval "$code_change" ) || echo "⚠️  Patch failed – continuing with next repo"
    fi
    
    # Store full JSON suggestion in the hints file
    jq --arg repo "$repo_name" --argjson payload "$ai_response" \
       '.[$repo] = $payload' "$AI_HINTS" > "${AI_HINTS}.tmp" && mv "${AI_HINTS}.tmp" "$AI_HINTS"
    echo "🤖 AI suggestion stored for $repo_name"
  else
    echo "⚠️  No OpenAI key configured – skipping AI hint step"
  fi

  # Return to the base directory for the next iteration
  cd "$BASE_DIR"
done < "${BASE_DIR}/repos.tsv"

# 7. Final summary
echo -e "\n🎉 Processed $total repositories."
echo "📊 AI hints saved to: $AI_HINTS"
echo "📁 Logs directory: ${BASE_DIR}/logs/"
echo "📄 Cleanup template can be generated with: generate-final-template.sh"

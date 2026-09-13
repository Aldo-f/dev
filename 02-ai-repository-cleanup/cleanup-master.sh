#!/usr/bin/env bash
# --------------------------------------------------------------
# cleanup‑master.sh – clean up one repository at a time with AI feedback
# --------------------------------------------------------------
set -euo pipefail

# ---------- 0️⃣ LOAD .env -------------------------------------------------
# Parse CLI flags
FORCE_YES="false"
while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes) FORCE_YES="true"; shift ;;
    *) echo "⚠️  Unknown option: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="${SCRIPT_DIR}/.env"

if [[ -f "$ENV_PATH" ]]; then
  source "$ENV_PATH"
  echo "Loaded configuration from $ENV_PATH"
else
  echo "No .env file found — using built-in defaults"
fi

# ---------- 1️⃣  DEFAULTS (overridden by .env) ----------
: "${BASE_DIR:=/mnt/HDD1/repository-cleanup-dir}"
: "${GITHUB_ORG:=Aldo-f}"
: "${GITLAB_GROUP:=Aldo-f}"
: "${REPO_LIMIT:=100}"
# ----------------------------------------------------------------

# 0. Verify required CLI tools are available
required_cmds=(gh glab jq git curl)
for cmd in "${required_cmds[@]}"; do
  command -v "$cmd" >/dev/null || {
    echo "❌ Missing dependency: $cmd – install it first"
    exit 1
  }
done

# Check if any AI CLI is available (hermes, opencode, claude)
ai_cli_available=false
for ai_cmd in hermes opencode claude; do
  if command -v "$ai_cmd" >/dev/null 2>&1; then
    ai_cli_available=true
    break
  fi
done

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
  glab repo list -u "$GITLAB_GROUP" -P "$REPO_LIMIT" -F json \
    | jq -r '.[] | ["gitlab", .name, .ssh_url_to_repo] | @tsv'
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
  # Try hermes chat --oneshot first (works via stdin)
  if command -v hermes >/dev/null; then
    echo "$prompt" | hermes chat -q - --oneshot 2>/dev/null
  elif command -v opencode >/dev/null; then
    opencode send "$prompt"
    opencode receive
  else
    echo '{"suggestion": "none", "code_change": ""}'
  fi
}

max_repos=${1:-3}
if [[ "$max_repos" -lt 1 ]]; then
  max_repos=3
fi


  # Skip repositories already marked for archiving
  if [[ "$repo_name" == *".archive" ]]; then
    echo "⏭️  Skipping $repo_name (already archived)"
    continue
  fi

  echo -e "\n=== [$platform] $repo_name ==="


  # Determine the target directory (preserve org/group hierarchy)
  target_dir="${BASE_DIR}/${platform}s/${repo_name}"
  mkdir -p "$(dirname "$target_dir")"
  if [[ -d "$target_dir/.git" ]]; then
    if [[ "$FORCE_YES" == "true" ]]; then
      echo "🔧 -y flag detected: using existing clone (no re‑clone)"
    else
      read -p "Repo already present at $target_dir. [r]e‑clone, [s]kip, [a]rchive, [c]ontinue? " choice
      case "$choice" in
        r|R) rm -rf "$target_dir" 2>/dev/null || true
        timeout 600 git clone "$repo_ssh" "$target_dir" 2>/dev/null || timeout 300 git clone "$repo_ssh" "$target_dir" 2>/dev/null || echo "❌ Re-clone failed for $repo_name – logging issue" || true
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
    fi
  else
    timeout 600 git clone "$repo_ssh" "$target_dir" 2>/dev/null || timeout 300 git clone "$repo_ssh" "$target_dir" 2>/dev/null || echo "❌ Clone failed for $repo_name (timeout/network) – logging issue" || true
  fi


  if [[ ! -d "$target_dir/.git" ]]; then
    echo "❌ Skipping $repo_name — clone did not complete at $target_dir"
    continue
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
  # Parse CLI flag to force yes response
  if [[ "$FORCE_YES" == "true" ]]; then
    echo "🔧 -y flag detected: auto-confirming cleanup for all repos"
  fi

  # 6.4 Ask the user whether to clean this repository (with -y flag support)
  if [[ "$FORCE_YES" == "true" ]]; then
    ans="y"
  else
    read -p "Do you want to clean $repo_name? (y/n/a) " ans
  fi
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
      timeout 1800 npm ci && timeout 1200 npx prettier --write . && timeout 1800 npm run lint || true
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

  # 6.5.4 Ensure README.md exists (skip repos without one)
    if [[ ! -f README.md ]]; then
      echo "❌ README.md not found in $repo_name – skipping repository"
      continue
    fi

  # 6.5.5 Extend .gitignore with generic ignore rules
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
    echo "Branch: ${cleanup_branch}"
    echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
    echo "Diff-stat:"
    git diff HEAD~1 HEAD --stat 2>/dev/null || echo "no diff"
    echo "=== END LOG ${repo_name} ==="
  } > "${log_file}"
  echo "📝 Log written → ${log_file}"

  # Merge cleanup branch into main/master immediately
  echo "🔀 Merging ${cleanup_branch} into main/master…"
  git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
  git checkout main 2>/dev/null || git checkout master 2>/dev/null || true
  git merge --no-ff "${cleanup_branch}" -m "Merge cleanup branch for ${repo_name}" || true
  git push origin main 2>/dev/null || git push origin master 2>/dev/null || true
  echo "🗑️  Deleting remote cleanup branch ${cleanup_branch}…"
  if ! git push origin --delete "${cleanup_branch}" 2>/dev/null; then
    echo "⚠️  Failed to delete remote cleanup branch ${cleanup_branch}"
  fi

  # ---------- AI FEEDBACK FOR NEXT REPO ----------
  if [[ "$ai_cli_available" == "true" ]]; then
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
    echo "⚠️  No AI CLI (hermes/opencode/claude) found – skipping AI hint step"
  fi

  # Return to the base directory for the next iteration
  # Increment processed count and stop after $max_repos repos
  processed_count=$((processed_count + 1))
  if [[ $processed_count -ge $max_repos ]]; then
    echo "🔚 Reached limit of $max_repos repositories – stopping."
    break
  fi

# 7. Final summary
echo -e "\n🎉 Processed $total repositories."
echo "📊 AI hints saved to: $AI_HINTS"
echo "📁 Logs directory: ${BASE_DIR}/logs/"
echo "📄 Cleanup template can be generated with: generate-final-template.sh"

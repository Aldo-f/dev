#!/usr/bin/env bash
# lib/repo_ops.sh – Repository cloning and cleanup operations
# --------------------------------------------------------------
# Usage: source this file, then call clone_repo, detect_stack, run_cleanup
# Requires: lib/env.sh to be sourced first

set -euo pipefail

clone_repo() {
  local platform="$1"
  local repo_name="$2"
  local repo_ssh="$3"
  local target_dir="${BASE_DIR}/${platform}s/${repo_name}"
  local force_yes="${4:-false}"

  mkdir -p "$(dirname "$target_dir")"

  if [[ -d "$target_dir/.git" ]]; then
    if [[ "$force_yes" == "true" ]]; then
      echo "🔧 -y flag: using existing clone"
    else
      read -p "Repo already present at $target_dir. [r]e‑clone, [s]kip, [a]rchive, [c]ontinue? " choice
      case "$choice" in
        r|R) rm -rf "$target_dir" 2>/dev/null || true
        timeout 600 git clone "$repo_ssh" "$target_dir" ;;
        s|S) echo "⏭️ Skipping $repo_name"; return 1 ;;
        a|A) local archived_dir="${target_dir}.archive"; mv "$target_dir" "$archived_dir"; echo "📦 Archived"; return 1 ;;
        *) echo "✅ Using existing clone" ;;
      esac
    fi
  else
    timeout 600 git clone "$repo_ssh" "$target_dir" 2>/dev/null || timeout 300 git clone "$repo_ssh" "$target_dir" 2>/dev/null || true
  fi

  if [[ ! -d "$target_dir/.git" ]]; then
    echo "❌ Clone failed for $repo_name"
    return 1
  fi

  echo "$target_dir"
}

detect_stack() {
  [[ -f "package.json" ]] && echo "node" && return
  [[ -f "requirements.txt" ]] && echo "python" && return
  [[ -f "go.mod" ]] && echo "go" && return
  [[ -f "pom.xml" ]] && echo "java-maven" && return
  echo "unknown"
}

run_cleanup() {
  local repo_name="$1"
  local target_dir="$2"
  local stack
  cd "$target_dir"

  stack=$(detect_stack)

  # Secret scan
  if command -v trufflehog >/dev/null; then
    trufflehog filesystem . > "${BASE_DIR}/${repo_name}_secrets.txt" 2>/dev/null || true
  fi

  # Lint / format
  case "$stack" in
    node)
      timeout 1800 npm ci 2>/dev/null || true
      timeout 1200 npx prettier --write . 2>/dev/null || true
      timeout 1800 npm run lint 2>/dev/null || true
      ;;
    python)
      pip install -r requirements.txt --quiet 2>/dev/null || true
      command -v black >/dev/null && black . 2>/dev/null || true
      command -v flake8 >/dev/null && flake8 . 2>/dev/null || true
      ;;
    go) go mod tidy && go fmt ./... ;;
    java-maven) mvn spotless:apply 2>/dev/null || true ;;
    *) echo "⚠️ Unknown stack – skipping lint/format" ;;
  esac

  # Ensure .env.example
  [[ -f .env.example ]] || echo "# Environment variables example" > .env.example
  # Ensure SECURITY.md
  [[ -f SECURITY.md ]] || cat > SECURITY.md <<'EOF'
# SECURITY

## Secrets
Never commit real secrets. All secrets must be supplied via environment variables (see `.env.example`).

## Dependencies
Run the relevant package‑manager audit command (npm audit, pip‑audit, go mod tidy, mvn dependency:analyze) and upgrade vulnerable versions.
EOF
  # Append .gitignore entries
  cat >> .gitignore << 'EOF'

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
}
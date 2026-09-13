#!/usr/bin/env bash
# --------------------------------------------------------------
# verify-setup.sh – quick sanity check before running cleanup
# --------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="${SCRIPT_DIR}/.env"

echo "Checking cleanup environment setup…"

errors=0
warnings=0

# 1. Check repository-local .env file
if [[ -f "$ENV_PATH" ]]; then
  echo "✅ Found .env at $ENV_PATH"
  source "$ENV_PATH"
else
  echo "❌ Missing repository-local .env file"
  ((errors++))
fi

# 2. Check required CLI tools
for cmd in gh glab jq git curl; do
  if command -v "$cmd" >/dev/null; then
    echo "✅ $cmd installed"
  else
    echo "❌ Missing dependency: $cmd"
    ((errors++))
  fi
done

# 3. Check AI CLI (optional but recommended)
ai_cli_found=false
if command -v hermes >/dev/null; then
  echo "✅ hermes installed"
  ai_cli_found=true
fi
if command -v opencode >/dev/null; then
  echo "✅ opencode installed"
  ai_cli_found=true
fi
if [[ "$ai_cli_found" == "false" ]]; then
  echo "⚠️  No AI CLI found (hermes/opencode) – will skip AI hints"
  ((warnings++))
fi

# 4. Check trufflehog (optional)
if command -v trufflehog >/dev/null; then
  echo "✅ trufflehog installed"
else
  echo "⚠️  trufflehog missing (optional)"
  warnings=$((warnings + 1))
fi

# 5. Check scripts exist and are executable (in 02-ai-repository-cleanup directory)
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for script in cleanup-master.sh generate-final-template.sh; do
  if [[ -x "${SCRIPT_DIR}/${script}" ]]; then
    echo "✅ ${script} executable"
  else
    echo "❌ ${script} missing or not executable"
    ((errors++))
  fi
done

# 6. Check target directory
TARGET="/mnt/HDD1/repository-cleanup-dir"
if [[ -d "$TARGET" ]]; then
  echo "✅ Target directory exists: $TARGET"
  if [[ -w "$TARGET" ]]; then
    echo "✅ Target directory is writable"
  else
    echo "❌ Target directory not writable"
    ((errors++))
  fi
else
  echo "❌ Target directory missing: $TARGET"
  ((errors++))
fi

# 7. Test syntax of scripts
if bash -n cleanup-master.sh 2>/dev/null; then
  echo "✅ cleanup-master.sh syntax valid"
else
  echo "❌ cleanup-master.sh has syntax errors"
  ((errors++))
fi

if bash -n generate-final-template.sh 2>/dev/null; then
  echo "✅ generate-final-template.sh syntax valid"
else
  echo "❌ generate-final-template.sh has syntax errors"
  ((errors++))
fi

# 8. Quick test: generate repos list without processing
echo ""
echo "🔎 Testing repo discovery (dry-run)…"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="${SCRIPT_DIR}/.env"
if [[ -f "$ENV_PATH" ]]; then
  source "$ENV_PATH"
fi
: "${BASE_DIR:=/mnt/HDD1/repository-cleanup-dir}"
: "${GITHUB_ORG:=Aldo-f}"
: "${GITLAB_GROUP:=Aldo-f}"
: "${REPO_LIMIT:=100}"

TMP_TSV=$(mktemp)
gh_output=$(gh repo list "$GITHUB_ORG" --limit "$REPO_LIMIT" --json name,sshUrl,visibility \
  | jq -r '.[] | ["github", .name, .sshUrl] | @tsv' 2>&1) || true
glab_output=$(glab repo list "$GITLAB_GROUP" -P "$REPO_LIMIT" --json name,sshUrl,visibility \
  | jq -r '.[] | ["gitlab", .name, .sshUrl] | @tsv' 2>&1) || true

echo "$gh_output" > "$TMP_TSV"
echo "$glab_output" >> "$TMP_TSV"

if [[ -f "$TMP_TSV" ]]; then
  count=$(wc -l < "$TMP_TSV")
  if [[ $count -gt 0 ]]; then
    echo "✅ Discovered $count repositories"
    # Show first 3 as sample
    echo "   Sample:"
    head -3 "$TMP_TSV" | while IFS=$'\t' read -r platform name url; do
      echo "   - [$platform] $name"
    done
  else
    echo "⚠️  No repositories found"
  fi
  rm -f "$TMP_TSV"
else
  echo "❌ Failed to create temp file"
  ((errors++))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
  echo "✅ All checks passed – ready to run!"
  echo ""
  echo "   bash cleanup-master.sh"
elif [[ $errors -eq 0 ]]; then
  echo "⚠️  Setup complete with $warnings warning(s)"
  echo "   bash cleanup-master.sh"
else
  echo "❌ $errors error(s) found – fix before running"
  exit 1
fi

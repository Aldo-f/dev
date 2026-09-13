#!/usr/bin/env bash
# --------------------------------------------------------------
# apply-readme-template.sh – inject README template into any repo
# --------------------------------------------------------------
set -euo pipefail

TEMPLATE="${1:-${SCRIPT_DIR}/README_template.md}"
TARGET_DIR="${2:-.}"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "❌ Template not found: $TEMPLATE"
  exit 1
fi

if [[ ! -f "$TARGET_DIR/README.md" ]]; then
  echo "❌ No README.md in $TARGET_DIR"
  exit 1
fi

# Replace the README.md with the template content
cp "$TEMPLATE" "$TARGET_DIR/README.md"
echo "✅ README.md updated from template: $TEMPLATE"
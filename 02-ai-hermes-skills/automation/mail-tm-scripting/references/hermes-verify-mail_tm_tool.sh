#!/bin/bash
set -e

SCRIPT="/home/aldo/scripts/form-automation/mail_tm_tool.sh"

# Check file exists
if [ ! -f "$SCRIPT" ]; then
  echo "FAIL: Script not found"
  exit 1
fi

# Check shebang
if ! head -n1 "$SCRIPT" | grep -q '^#!/bin/bash$'; then
  echo "FAIL: Not a bash script"
  exit 1
fi

# Check for curl command
if ! grep -q 'curl -s -u' "$SCRIPT"; then
  echo "FAIL: curl command missing"
  exit 1
fi

# Check for jq usage
if ! grep -q 'jq' "$SCRIPT"; then
  echo "FAIL: jq not used"
  exit 1
fi

# Check for correct email domain
if ! grep -q 'chiefmommy@mail.tm' "$SCRIPT"; then
  echo "FAIL: Email domain should be @mail.tm"
  exit 1
fi

echo "PASS: Script syntax and key components verified"
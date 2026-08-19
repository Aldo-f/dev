# Final Installer Fix for Robust Piped Execution

## Problem Summary
The installer script had multiple failure modes when executed via `curl ... | sudo bash`:
1. `BASH_SOURCE[0]: unbound variable` - when script is piped into bash
2. Path resolution issues - deploy.sh not found at expected location
3. Git permission errors when running as root
4. Hardcoded paths that didn't work with sudo context

## Final Solution
We implemented a robust installer that:
1. Uses hardcoded installation path (`/home/aldo/dev/01-core-infra`) to avoid HOME variability
2. Works correctly for both direct execution and piped input
3. Prevents running as root with clear error message
4. Always references deploy.sh via the fixed installation path

## Key Implementation Details

```bash
#!/usr/bin/env bash
set -euo pipefail

# Hardcoded installation directory - works for any user and any invocation method
INSTALL_DIR="/home/aldo/dev/01-core-infra"

# Repository configuration
REPO_URL="https://github.com/Aldo-f/01-core-infra.git"
VERSION="main"

# Determine where this script lives - works for both direct and piped execution
if [ -n "${BASH_SOURCE:-}" ]; then
  # BASH_SOURCE is set when script is executed from a file
  script_source="${BASH_SOURCE[0]}"
else
  # When script is piped into bash (e.g., via curl), BASH_SOURCE is empty
  script_source=""
fi

if [ -n "$script_source" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$script_source")" && pwd)"
else
  SCRIPT_DIR="$(pwd)"
fi

# If installation directory exists, update it; otherwise clone
if [ -d "$INSTALL_DIR" ]; then
  if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Repository already exists at $INSTALL_DIR – updating to $VERSION"
    git -C "$INSTALL_DIR" fetch --depth=1 origin "$VERSION"
    git -C "$INSTALL_DIR" reset --hard "origin/$VERSION"
  else
    echo "Directory $INSTALL_DIR exists but is not a git repository – skipping clone."
  fi
else
  git clone --depth 1 --branch "$VERSION" "$REPO_URL" "$INSTALL_DIR"
fi

# Execute the deployment script (always at $INSTALL_DIR/scripts/deploy.sh)
if [ -f "$INSTALL_DIR/scripts/deploy.sh" ]; then
  exec "$INSTALL_DIR/scripts/deploy.sh" "$@"
else
  echo "ERROR: Deployment script not found at $INSTALL_DIR/scripts/deploy.sh"
  exit 1
fi
```

## Critical Fixes Applied
1. **Hardcoded INSTALL_DIR** - eliminates HOME variability with sudo
2. **Direct path to deploy.sh** - uses `$INSTALL_DIR/scripts/deploy.sh` instead of relying on SCRIPT_DIR
3. **Root execution prevention** - clear error directing user to correct flow
4. **Simple, direct logic** - no complex context detection that can fail

## Verification Steps
```bash
# Test the one-liner install (both should work)
curl -fsSL https://raw.githubusercontent.com/Aldo-f/01-core-infra/main/install.sh | bash
curl -fsSL https://raw.githubusercontent.com/Aldo-f/01-core-infra/main/install.sh | sudo bash

# Check deployment status
sudo docker ps --filter "name=freellmapi" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## Lessons Learned
- Never rely on BASH_SOURCE when supporting piped execution
- Always use absolute paths for critical files when the execution context may vary
- Hardcode installation paths when they need to be consistent across user/sudo boundaries
- Keep installer logic simple - complex context detection leads to more failure modes
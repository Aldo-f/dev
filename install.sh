#!/usr/bin/env bash
set -e

# Ensure git is installed (needed for cloning if we are not in a repo)
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    apt-get update && apt-get install -y git
fi

# Determine the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we are already in the repo (i.e., 01-core-infra/install.sh exists relative to this script)
if [[ -f "${SCRIPT_DIR}/01-core-infra/install.sh" ]]; then
    # We are in the repo root, run the real install.sh
    echo "Running install.sh from existing repository..."
    cd "${SCRIPT_DIR}/01-core-infra" && ./install.sh
else
    # We are likely being run via curl | bash, so clone the repo to ~/dev
    echo "Cloning repository to ~/dev..."
    git clone https://github.com/Aldo-f/dev.git ~/dev
    # Then run the real install.sh from the cloned repo
    cd ~/dev/01-core-infra && ./install.sh
fi
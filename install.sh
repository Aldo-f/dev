#!/usr/bin/env bash
# Wrapper install script for the Aldo-f/dev monorepo (now using submodules)
# This script ensures we are in the repo root, initializes submodules, and runs the core infra install.

set -euo pipefail

# Change to the directory where this script is located (the repo root)
cd "$(dirname "$0")"

# Initialize and update submodules
git submodule update --init --recursive

# Run the core infra install script
./01-core-infra/install.sh "$@"

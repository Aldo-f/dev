#!/usr/bin/env bash
set -e

# Determine the script's directory and change to the 01-core-infra subdirectory
cd "$(dirname "$0")/01-core-infra" && ./install.sh
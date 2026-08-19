#!/usr/bin/env bash
set -euo pipefail

# 01-core-infra installer — pure-Ansible editie.
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "=== Initializing Ansible-based deployment ==="

# Zorg dat Ansible en Git aanwezig zijn
if ! command -v ansible-playbook >/dev/null 2>&1; then
    log "Ansible ontbreekt — installeren..."
    sudo apt-get update -qq
    sudo apt-get install -y ansible git
fi

# Parse CLI flags so we can forward them to ansible-playbook.
# Usage examples:
#   ./install.sh                                # run everything
#   ./install.sh --tags containers              # only the containers role
#   ./install.sh --tags containers -e 'limit_services=["05-media-jellyfin"]'
TAGS_FLAG=""
EXTRA_VARS_FLAG=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tags)
            TAGS_FLAG="--tags $2"
            shift 2
            ;;
        --limit-services)
            EXTRA_VARS_FLAG="$EXTRA_VARS_FLAG -e limit_services=$2"
            shift 2
            ;;
        -e|--extra-vars)
            EXTRA_VARS_FLAG="$EXTRA_VARS_FLAG -e '$2'"
            shift 2
            ;;
        *)
            # Forward any other ansible-playbook flag verbatim
            EXTRA_VARS_FLAG="$EXTRA_VARS_FLAG $1"
            shift
            ;;
    esac
done

# Uitvoeren playbook
cd "$(dirname "$0")/../ansible"
log "=== Running Ansible playbook (tags='${TAGS_FLAG:-all}' extra-vars='${EXTRA_VARS_FLAG:-<none>}') ==="
ansible-playbook -i inventories/local.yml playbooks/site.yml $TAGS_FLAG $EXTRA_VARS_FLAG

log "=== Deployment completed successfully ==="

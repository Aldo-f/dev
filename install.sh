#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# dev monorepo installer — THE one bootstrap/update entrypoint.
#
#   curl -o- https://raw.githubusercontent.com/Aldo-f/dev/main/install.sh | bash
#
# Behaviour:
#   - Fresh machine            -> clones ~/dev, then runs the Ansible playbook
#   - Existing clean checkout  -> fast-forwards to origin/main, runs playbook
#   - Existing dirty checkout  -> auto-stashes tracked changes, fast-forwards,
#                                 pops the stash back (conflicts stay SAFE in
#                                 the stash; script tells you how to recover)
#   - INSTALL_SKIP_IF_DIRTY=1  -> skips the git update entirely when dirty
#   - Unpushed commits         -> update skipped, nothing touched
# Flags are forwarded to ansible-playbook:
#   ./install.sh --tags containers --limit-services '["05-media-jellyfin"]'
# ============================================================================

REPO_URL="https://github.com/Aldo-f/dev.git"
DEV_DIR="${HOME}/dev"
BRANCH="main"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# Sync a checkout to origin/<branch> WITHOUT destroying local work.
safe_sync() {
    local dir="$1" branch="${2:-main}"
    # NOTE: no --depth here. A shallow fetch grafts origin/<branch> to a single
    # commit, which breaks merge-base ancestry checks below and makes every
    # "behind" state look like "unpushed commits".
    git -C "$dir" fetch origin "$branch"

    # Only update when local is behind or equal (no unpushed commits).
    if ! git -C "$dir" merge-base --is-ancestor HEAD "origin/$branch"; then
        echo "⚠  Local repository has unpushed commits — skipping git update."
        echo "   (Run 'git push origin $branch' to sync first.)"
        return 0
    fi

    # Already at origin — nothing to do (never churn the working tree).
    if git -C "$dir" merge-base --is-ancestor "origin/$branch" HEAD; then
        echo "✓ Repository is up to date with origin/$branch."
        return 0
    fi

    if [ -z "$(git -C "$dir" status --porcelain --untracked-files=no)" ]; then
        git -C "$dir" reset --hard "origin/$branch"
        return 0
    fi

    if [ "${INSTALL_SKIP_IF_DIRTY:-0}" = "1" ]; then
        echo "⚠  Local changes present — skipping update (INSTALL_SKIP_IF_DIRTY=1)."
        return 0
    fi

    echo "⚠  Local changes present — stashing them before update..."
    local stash_before stash_after
    stash_before="$(git -C "$dir" rev-parse -q --verify refs/stash 2>/dev/null || true)"
    if ! git -C "$dir" stash push -m "install.sh auto-stash $(date '+%F %T')"; then
        stash_after="$(git -C "$dir" rev-parse -q --verify refs/stash 2>/dev/null || true)"
        if [ -n "$stash_after" ] && [ "$stash_after" != "$stash_before" ]; then
            echo "ERROR: a stash entry was created but the working tree could not be" >&2
            echo "       fully updated (unreadable/root-owned files?). Your changes are" >&2
            echo "       SAFE in 'git stash' — recover them with 'git stash pop'." >&2
            exit 1
        fi
        echo "ERROR: could not stash local changes — aborting update. Nothing was destroyed." >&2
        exit 1
    fi
    git -C "$dir" reset --hard "origin/$branch"

    local pop_out
    if pop_out="$(git -C "$dir" stash pop 2>&1)"; then
        echo "✓ Local changes restored on top of origin/$branch."
    else
        echo "⚠  Could not restore stashed changes automatically — they are SAFE in the stash:" >&2
        git -C "$dir" stash list | head -3 >&2
        echo "$pop_out" >&2
        echo "   Resolve manually with 'git stash pop'." >&2
    fi
}

apt_install() {
    if [ "$(id -u)" -eq 0 ]; then apt-get install -y "$@"; else sudo apt-get install -y "$@"; fi
}

# --- Locate (or create) the checkout ---------------------------------------
SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"
SCRIPT_DIR=""
if [ -n "$SCRIPT_SOURCE" ] && [ -f "$SCRIPT_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
fi

REPO_DIR=""
if [ -n "$SCRIPT_DIR" ] && [ -d "${SCRIPT_DIR}/.git" ] \
       && [ -f "${SCRIPT_DIR}/01-core-infra/ansible/playbooks/site.yml" ]; then
    # Invoked from inside an existing checkout — use it.
    REPO_DIR="${SCRIPT_DIR}"
    log "Using existing repository at ${REPO_DIR}..."
    safe_sync "${REPO_DIR}" "${BRANCH}"
elif [ -d "${DEV_DIR}/.git" ]; then
    # ~/dev already exists — update it safely.
    REPO_DIR="${DEV_DIR}"
    log "~/dev already exists — updating repository safely..."
    safe_sync "${REPO_DIR}" "${BRANCH}"
else
    # Fresh machine — ensure git, clone.
    if ! command -v git >/dev/null 2>&1; then
        log "Installing git..."
        apt-get update -qq || sudo apt-get update -qq
        apt_install git
    fi
    log "Cloning repository to ${DEV_DIR}..."
    git clone --depth 1 -b "${BRANCH}" "${REPO_URL}" "${DEV_DIR}"
    REPO_DIR="${DEV_DIR}"
fi

# --- Deploy -----------------------------------------------------------------
INFRA_DIR="${REPO_DIR}/01-core-infra"
[ -f "${INFRA_DIR}/ansible/playbooks/site.yml" ] || {
    echo "ERROR: playbook not found at ${INFRA_DIR}/ansible/playbooks/site.yml" >&2
    exit 1
}

if ! command -v ansible-playbook >/dev/null 2>&1; then
    log "Ansible missing — installing..."
    apt-get update -qq || sudo apt-get update -qq
    apt_install ansible git
fi

# Parse CLI flags so we can forward them to ansible-playbook.
TAGS_FLAG=""
EXTRA_VARS_FLAG=""
while [ $# -gt 0 ]; do
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

log "=== Running Ansible playbook (tags='${TAGS_FLAG:-all}' extra-vars='${EXTRA_VARS_FLAG:-<none>}') ==="
cd "${INFRA_DIR}/ansible"
ansible-playbook -i inventories/local.yml playbooks/site.yml $TAGS_FLAG $EXTRA_VARS_FLAG

log "=== Deployment completed successfully ==="

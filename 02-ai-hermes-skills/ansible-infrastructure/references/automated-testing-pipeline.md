# Automated Testing Pipeline for 01-core-infra (SDD/TDD)

## Overview
A complete 4-stage automated testing pipeline following Spec-Driven Development (SDD) methodology, implemented for the 01-core-infra Ansible project. This pipeline provides Test-Driven Development (TDD) capabilities for infrastructure code.

## Architecture: Four Stages

### Stage 1: Pre-commit (Local - Husky)
Fast validation before every commit (< 30 seconds):
- **Hook**: `.git/hooks/pre-commit`
- **Checks**: `ansible-lint` + playbook syntax check
- **Command**: `make lint syntax`
- **Installed via**: `make install-hooks`

```bash
# Pre-commit hook location
/home/aldo/dev/01-core-infra/.git/hooks/pre-commit
```

### Stage 2: CI Pipeline (GitHub Actions)
Full integration testing on every PR/push:
- **Workflow**: `.github/workflows/test-infra.yml`
- **Matrix**: Tests with `aldo` and `testuser1` (validates placeholder resolution)
- **Environment**: Fresh LXD Ubuntu 22.04 containers per test
- **Progress**: Real-time GitHub Step Summaries with timing
- **Artifacts**: Automatic upload on failure (logs, hermes dir, lxd logs)

```yaml
# Key workflow features
strategy:
  fail-fast: false
  matrix:
    user: [aldo, testuser1]
```

### Stage 3: Progress Monitoring
- **GitHub Actions**: Step summaries with step-by-step timing
- **Local**: Colored output via `progress_tracker.py`
- **Optional**: Slack/Discord notifications on failure

### Stage 4: Periodic Regression
- **Schedule**: Weekly (Monday 2 AM UTC)
- **Catches**: Infrastructure drift, package updates breaking compatibility

## Test Coverage

The test suite validates 20+ checks:

| Category | Checks |
|----------|--------|
| Playbook | Syntax, linting, dry-run, full execution |
| Systemd | Unit deployment with placeholder resolution, service activation, port listening |
| Network | HTTP endpoints, Traefik routes.yml quoting |
| Packages | docker.io, locate, jq, git, curl |
| Groups | www-data membership |
| Idempotency | Second run reports `changed=0` |
| Placeholders | Multi-user resolution (`core_infra_home`, `core_infra_user`, `core_infra_root`) |
| Media | Container deployment, Traefik network, Nextcloud health |

### Updates (2026-08-13)
- **Nextcloud container name fixed**: Verification now checks for `05-media-nextcloud-app-1` (Docker Compose project prefix) instead of `nextcloud` or `nextcloud-app-1`
- **Package detection fixed**: Uses `dpkg -l | grep -q <package>` instead of `check_package_installed()` function to avoid false negatives
- **Routes verification updated**: Checks for `cloud.aldof.duckdns.org` (Nextcloud) instead of `nextcloud.aldof.duckdns.org`
- **All 17 checks pass**: Including media containers, Traefik routes, systemd units, and required packages

## Key Files

| File | Purpose |
|------|---------|
| `tests/run_playbook_test.sh` | Main TDD driver - LXD container, multi-user |
| `tests/verify_deployment.py` | 20+ post-deployment validation checks |
| `tests/progress_tracker.py` | Real-time progress for GitHub + local |
| `.github/workflows/test-infra.yml` | CI pipeline with multi-user matrix |
| `.git/hooks/pre-commit` | Husky-compatible pre-commit hook |
| `Makefile` | Convenience targets (see below) |
| `package.json` | npm scripts mapping + husky dev dep |

## Makefile Targets

```bash
# Quick checks (no container)
make lint syntax dry-run

# Full TDD suite
make test              # LXD container with current user
make test-multi-user   # Validates placeholders across users

# Deploy & verify
make deploy
make verify

# Utilities
make install-hooks
make clean
```

## Cross-Device Placeholders

Implemented in all systemd templates (`.service.j2`):

```yaml
# In ansible/playbooks/site.yml
core_infra_home: "/home/aldo"
core_infra_user: "aldo"
core_infra_root: "/var/lib/core-infra"
```

Template usage:
```jinja2
WorkingDirectory={{ core_infra_home }}
User={{ core_infra_user }}
ExecStart={{ core_infra_root }}/llama.cpp/build/bin/llama-server ...
```

## Traefik Quoting Fix

Prevents the regex clobbering bug (from memory):
```yaml
# Correct format in routes.yml
rule: "Host(`plex.aldof.duckdns.org`)"

# Incorrect (causes 404):
rule: Host(`plex.aldof.duckdns.org`)
```

Validation in `verify_deployment.py`:
```python
pattern = rf'rule:\s*"Host\(`{re.escape(host)}`\)"'
```

## LXD Networking Fixes

Container DNS and connectivity issues resolved:

```bash
# In run_playbook_test.sh
sudo /usr/bin/lxc exec "$CONTAINER" -- bash -c "echo 'nameserver 212.224.129.90
nameserver 212.224.129.94' > /etc/resolv.conf"
```

## CI Pipeline Features

1. **Concurrency control**: Cancel in-progress runs on same ref
2. **Timeout**: 60 minutes per matrix job
3. **Failure artifacts**: Upload `~/.hermes/`, `/var/log/lxd/`
4. **Validation job**: Runs after test matrix completes
5. **Notifications**: Optional Slack/Discord on failure

## Verification Script Usage

```bash
# Full verification
python3 tests/verify_deployment.py --core-infra-root /var/lib/core-infra --test-user aldo

# Check-only mode (non-zero exit on failure but no error exit)
python3 tests/verify_deployment.py --check-only
```

## Progress Tracker Usage

```python
from tests.progress_tracker import ProgressTracker

tracker = ProgressTracker()
tracker.start_step("Syntax Check", "Checking playbook syntax")
tracker.complete_step('passed')
tracker.start_step("Lint Check", "Running ansible-lint")
tracker.complete_step('passed')
# ... etc
tracker.print_final_summary()
```

## SPEC.md

Full specification document at project root: `SPEC.md` - contains requirements, architecture, and implementation plan following spec-kit methodology.

## Usage in Development Workflow

```bash
# 1. Before commit (auto via hook)
git commit -m "..."  # Runs lint + syntax

# 2. Local TDD cycle
make test              # Full test suite
# Fix failures
make test              # Re-run until green

# 3. Push triggers CI
git push origin feature-branch
# GitHub Actions runs full matrix

# 4. Weekly regression runs automatically
# (Monday 2 AM UTC)
```

## Troubleshooting

### LXD Not Available
```bash
# Install on host
sudo apt-get update && sudo apt-get install -y lxd
sudo lxd init --auto
```

### Pre-commit Fails
```bash
# Run manually to debug
make lint syntax
```

### CI Fails on DNS
Check `run_playbook_test.sh` DNS configuration section - uses hardcoded nameservers that may need adjustment for different networks.

### Placeholder Resolution Issues
Verify templates use `{{ core_infra_home }}`, `{{ core_infra_user }}`, `{{ core_infra_root }}` - not old `__HOME__`, `__USER__`, `__CORE_INFRA__` syntax.

## Future Enhancements

- [ ] Add performance benchmarks to verification
- [ ] Integrate with spec-kit MCP for spec validation
- [ ] Add chaos testing (container kill, network partition)
- [ ] Expand matrix to more users/distros (Debian, Alpine)
---
name: git-workflow-troubleshooting
description: "Fix git permission, ownership, and remote issues."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Git, Troubleshooting, Permissions, SSH]
    related_skills: [github-repo-management, github-auth]
---

# Git Workflow Troubleshooting

This skill covers common git patterns and pitfalls experienced when working in Linux environments, specifically dealing with permission issues and remote management.

## 1. Permission & Ownership Fixes

When install scripts or automated tools run with `sudo`, they often leave `.git` directories owned by `root`.

### Fix Root-owned `.git` directories
If you cannot push, pull, or commit, check ownership:
```bash
ls -la .git
```
If you see `root` as the owner, run:
```bash
sudo chown -R $USER:$USER .git
```

### Installation Best Practices
*   **Run as user:** Avoid `sudo bash` for install scripts unless strictly required. Use `bash` instead, letting the script request `sudo` only for specific system-level commands (apt, systemd, etc.).

## 2. Remote Management for Upstream Repositories

When working with repositories you do not own (upstream), you cannot push directly to `origin`.

### Manual Workflow
1.  **Keep `origin` (HTTPS/Readonly):** Use it for `git pull` and `git fetch`.
2.  **Add a `fork` (SSH/Readwrite):**
    ```bash
    git remote add fork git@github.com:<your-username>/<repo-name>.git
    ```
3.  **Push to `fork`:**
    ```bash
    git push fork <branch-name>
    ```

### Automated Upstream Sync via GitHub Actions

To keep a fork automatically in sync with the upstream repository (e.g., daily), create a workflow file at `.github/workflows/sync-upstream.yml`:

```yaml
name: Sync Upstream
on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  workflow_dispatch: # Allow manual trigger
jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Sync Upstream
        uses: dabreadman/sync-upstream-repo@v1.3.0
        with:
          upstream_repo: owner/repo-name
          upstream_branch: master
          branch: master
          token: ${{ secrets.GITHUB_TOKEN }}
```

> **Note:** Always perform your own work on a separate branch (not `master`) to avoid conflicts during the automated sync.

## 3. SSH Authentication Issues

If SSH authentication fails:

### Verify Key
```bash
cat ~/.ssh/id_ed25519.pub
# Ensure this key is added to your GitHub account
```

### SSH Agent
If `git` keeps asking for a password, load your key into the agent:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

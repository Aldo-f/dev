---
name: github-fork-sync
description: "Automated fork synchronization using custom GitHub Actions."
tags: [GitHub, Fork, Sync, Upstream, CI/CD, Actions]
version: 1.1.0
---
# GitHub Fork Sync

Use this procedure to automate synchronization of your forks with upstream repositories, avoiding unreliable third-party marketplace actions.

See `references/upstream-sync.md` for the complete workflow implementation with key fixes and pitfalls.
Use `templates/sync-upstream.yml` as a ready-to-copy starter (replace `<OWNER>/<REPO>` with the upstream).

## Quick Debugging Checklist

When a sync workflow fails:
1. Check `gh run view <run_id> --log` for the actual error
2. Common issues:
   - **Typo in `--exit-code`** — must be `--exit-code`, not `--exit-data`
   - **Missing `workflows: write` permission** — needed when upstream modifies workflow files
   - **Git config missing** — add bot user.name/user.email for clean merge commits
3. Manual dispatch via `gh workflow run` may show schema error for `workflows: write` (outdated schema), but scheduled runs work correctly

# Fork Upstream Sync Workflow

For repositories that need to stay in sync with an upstream source (e.g., forks of public repositories), avoid unreliable marketplace actions. Use a robust GitHub Action workflow that performs a merge.

Create `.github/workflows/sync-upstream.yml`:

```yaml
name: Sync Upstream
on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      workflows: write
    steps:
      - name: Checkout Fork
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0

      - name: Sync Upstream
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git remote add upstream https://github.com/<owner>/<repo>.git
          git fetch upstream
          git checkout master
          # Only merge if upstream has new commits
          if git diff --quiet upstream/master --exit-code; then
            echo "Already up to date with upstream"
          else
            git merge upstream/master --no-edit
            git push origin master
          fi
```

## Key Fixes (from debugging session)

1. **`--exit-code` not `--exit-data`** — The typo caused `git diff` to print usage and exit 1, making the merge always run unnecessarily.

2. **`workflows: write` permission** — Required when upstream has workflow file changes (`.github/workflows/*.yml`). Without this, pushes that modify workflow files are rejected with "refusing to allow a GitHub App to create or update workflow without `workflows` permission".

3. **Conditional merge with `--exit-code`** — Avoids creating empty merge commits when already up to date.

4. **Git config for bot identity** — Ensures clean commit authorship for automated merges.

## Pitfalls

- The `workflows: write` permission may trigger a schema validation error when manually dispatching via `gh workflow run` (outdated schema), but scheduled runs execute the workflow directly from the repo and work correctly.
- GitHub Actions token must have Contents: Write (provided by default with `secrets.GITHUB_TOKEN`).
- If the fork is significantly diverged, manual intervention may be needed.
# 02-ai-repository-cleanup

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J2Z126OL9C)

A Bash pipeline for bulk-cleaning GitHub and GitLab repositories under the `Aldo-f` organization/group.

## What it does

- Discovers repositories with `gh` and `glab`
- Clones each repo into `${BASE_DIR}/${platform}s/<repo>`
- Runs stack-aware cleanup:
  - Node: `npm ci`, `npm run lint`, `npx prettier --write .`
  - Python: `pip install -r requirements.txt`, `black`, `flake8`
  - Go: `go mod tidy`, `go fmt ./...`
  - Maven: `mvn spotless:apply`
- Ensures `.env.example`, `SECURITY.md`, and generic `.gitignore` entries exist
- Commits changes on `cleanup/YYYYMMDD-<repo>`
- Merges into `main`/`master`, pushes, and attempts to delete the remote cleanup branch
- Writes per-repo logs to `${BASE_DIR}/logs/`

## Requirements

- `gh`
- `glab`
- `jq`
- `git`
- `curl`
- Optional: `hermes`, `opencode`, or `claude` for AI feedback
- Optional: `trufflehog` for secret scanning

GitHub and GitLab authentication must be configured before running the full pipeline.

## Configuration

Create a `.env` file in the repository root (same directory as this README and the cleanup scripts). Example content:

```bash
BASE_DIR="/mnt/HDD1/repository-cleanup-dir"
GITHUB_ORG="Aldo-f"
GITLAB_GROUP="Aldo-f"
REPO_LIMIT=100
```

## Quick start

```bash
cd /home/aldo/dev/02-ai-repository-cleanup
bash verify-setup.sh
bash cleanup-master.sh -y
```

Use `cleanup-test.sh` for a safe demo run:

```bash
REPO_LIMIT=3 bash cleanup-test.sh -y
```

The test script processes the first 3 repositories from `repos.tsv` and does not push changes.

## Main scripts

- `cleanup-master.sh` — full multi-repo cleanup pipeline
- `cleanup-test.sh` — limited non-interactive demo run
- `verify-setup.sh` — preflight checks for tools, config, and syntax
- `apply-readme-template.sh` — injects `README_template.md` into a repository
- `generate-final-template.sh` — builds a reusable cleanup template from collected AI hints

## Safety notes

- Review changes before running on important repositories.
- `cleanup-master.sh -y` skips interactive confirmations.
- The script commits and pushes cleanup branches automatically.
- Repos without `README.md` are skipped.
- Missing `npm run lint` scripts are tolerated and logged.
- Clone and npm steps use bounded timeouts.
- The merge step pulls from `origin/main` or `origin/master` first to avoid non-fast-forward failures.
- Remote cleanup branches are deleted after merge when possible.
- The `.env` file must be present in the repository root for the script to load configuration; if missing, the script continues with defaults and logs any issues.

## Logs and AI hints

Per-repo logs are written to:

```text
${BASE_DIR}/logs/<repo>.txt
```

When an AI CLI is available, improvement hints are stored in:

```text
${BASE_DIR}/ai-hints.json
```

## Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/J2Z126OL9C)
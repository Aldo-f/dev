# Automated Repository Cleanup with AI Feedback

A script to systematically clean up all your GitHub and GitLab repositories, with iterative improvement suggestions from AI.

## Quick Start

### 1. Install Dependencies
```bash
# Check required tools
gh version
glab version
trufflehog version
jq --version
hermes --version  # or: opencode --version
```

### 2. Configure
Edit `~/.hermes/cleanup.env`:
```dotenv
BASE_DIR="/mnt/HDD1/dev"
GITHUB_ORG="Aldo-f"
GITLAB_GROUP="Aldo-f"
REPO_LIMIT="500"
AI_MODEL="gpt-4o-mini"
OPENAI_API_KEY=""  # optional – leave empty to skip AI hints
```

### 3. Authenticate
```bash
gh auth login
glab auth login
```

### 4. Start AI Session (Optional but Recommended)
Open a new terminal and start a persistent session:
```bash
hermes chat --session cleanup-session
# OR
opencode chat --session cleanup-session
```

**Keep this terminal open** while running the cleanup script.

### 5. Run Cleanup
```bash
cd ~/dev
bash cleanup-master.sh
```

The script will:
- Clone each repository to `/mnt/HDD1/dev/<platform>/<repo>`
- Ask you to confirm cleanup per repo
- Run lint, format, secret scan
- Commit changes to a `cleanup/<date>-<repo>` branch
- Ask AI for improvement suggestions (if API key configured)

## Post-Processing

After all repos are processed:

```bash
# Generate the final reusable template
bash generate-final-template.sh

# Review collected AI hints
cat ~/dev/ai-hints.json

# View logs
ls -la /mnt/HDD1/dev/logs/
```

## Usage Without AI

Set `OPENAI_API_KEY=` (empty) in `.env` and the script will run without asking AI for suggestions.

## Files

| File | Purpose |
|------|---------|
| `cleanup-master.sh` | Main orchestrator script |
| `generate-final-template.sh` | Creates reusable template from hints |
| `~/.hermes/cleanup.env` | Configuration |
| `~/dev/ai-hints.json` | Collected AI suggestions |
| `/mnt/HDD1/dev/logs/` | Per-repository cleanup logs |
| `/mnt/HDD1/dev/cleanup-template.sh` | Final reusable script |

## Troubleshooting

- **"No .env file found"**: Create `~/.hermes/cleanup.env`
- **Permission denied on `/mnt/HDD1`**: Check that your user has write access
- **CLI tool not found**: Install the missing dependency first
- **AI session closed**: Script will continue without suggestions – just run `generate-final-template.sh` afterwards

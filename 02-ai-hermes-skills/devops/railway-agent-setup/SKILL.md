---
name: railway-agent-setup
description: Use when installing Railway CLI with agent support.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [railway, cli, deployment, devops]
    related_skills: [ansible-infrastructure]
---

# Railway Agent Setup

## Overview

This skill covers the complete workflow for installing Railway CLI with agent support, configuring authentication, and linking to projects. The Railway CLI enables command-line interaction with Railway projects and includes built-in agent skills for Claude Code, Cursor, OpenAI Codex, OpenCode, and GitHub Copilot.

## When to Use

- Setting up Railway CLI with agent support for the first time on a new machine
- Re-configuring agent tools after a reinstallation
- Linking existing projects after authentication
- Troubleshooting offline agent service status

## Prerequisites

- Linux, macOS, or Windows (via WSL)
- Network connectivity to `railway.com`
- A Railway account and at least one project

## Installation

### Standard Installation (with agent tools)

```bash
bash <(curl -fsSL railway.com/install.sh) --agents -y
```

This installs:
- CLI to `~/.railway/bin`
- Shell PATH configuration (supports fish, bash, zsh)
- Agent skills for supported coding tools
- Local Railway MCP server

### Verify Installation

```bash
# Source the fish config or add to PATH manually
export RAILWAY_HOME=/home/aldo/.railway
export PATH="$RAILWAY_HOME/bin:$PATH"

railway --version
# Expected: railway 5.x.x
```

## Authentication

The login process requires an interactive browser session. If running in a headless environment, use the pre-generated activation code:

```bash
railway login
# Outputs: https://railway.com/activate?user_code=XXXX-XXXX
# Open this URL in a browser and enter the code
```

## Project Linking

### Interactive Linking

```bash
railway link
```

This opens an interactive prompt to select workspace and project.

### Non-Interactive Linking

```bash
# List available projects
railway projects list

# Link to a specific project by name
railway link --project <project-name>
```

### Programmatic Linking

```bash
# Get workspace and project IDs first
railway project status

# Then link explicitly
railway link --workspace <workspace-name> --project <project-name> --environment <env-name>
```

## Service Management

### Check Service Status

```bash
railway status
```

Output includes:
- Workspace and project details
- Environment information
- Service status and URL
- Volume usage

### Start/Stop Services

There are NO `start`/`stop` subcommands. Use the service ID (not the service name) for all service-level operations:

```bash
# Get the service ID (this is required for logs/restart)
railway service list            # shows service ID + current status
railway status                  # shows linked project, env, service, URL

# Fetch logs — MUST use the service ID, not the name
railway logs --service <service-id> --tail 50

# Redeploy/restart — MUST use the service ID, not the name
railway restart --service <service-id>

# Remove the most recent deployment
railway down
```

**Service vs deployment lifecycle**: `railway status` reporting `○ Offline` does NOT mean you can restart it with a start command. Check deployment history to see whether the service actually has a live deployment:

```bash
railway deployment list --service <service-id>
# → "RECENT" (running), "DEPLOYING", "CRASHING", or "REMOVED"
```

If the last deployment shows `REMOVED` with no active deployment, there is no instance running — logs will come back empty and there is nothing to restart. You need to deploy fresh (see troubleshooting below).

## Agent Skill Verification

After installation, verify agent skills are configured:

```bash
railway setup agent -y
# Checks for:
# - Railway skills in supported IDEs/tools
# - Railway MCP server configuration
# - Authentication status
```

## Common Pitfalls

1. **PATH not updated in non-fish shells**: The installer writes fish config. For bash/zsh, manually add to ~/.bashrc:
   ```bash
   export RAILWAY_HOME="$HOME/.railway"
   export PATH="$RAILWAY_HOME/bin:$PATH"
   ```

2. **Login times out waiting for browser**: This is normal - the command blocks waiting for you to complete authentication in the browser. Use `bg` to run in background if needed.

3. **Project not linked (No linked project found)**: Run `railway link` to connect to a project first.

4. **Hermes Agent service shows Offline**: Do NOT treat this as "normal" — investigate. Run `railway deployment list --service <service-id>` to check for a live deployment. `○ Offline` with the last deployment `REMOVED` means no instance is running and nothing can be restarted; you must redeploy fresh using `railway deploy` (template) or the project config.

5. **Volume capacity issues**: Check volume usage with `railway volume list`. Consider upgrading if approaching 100% capacity.

6. **Fish `set` command errors**: The env.fish uses fish syntax. For bash, use `export` commands instead:
   ```bash
   export RAILWAY_HOME=/home/aldo/.railway
   export PATH="$RAILWAY_HOME/bin:$PATH"
   ```

7. **`railway deploy -t <template>` says "Template not found"**: `-t` expects a template code, not an arbitrary repo name, and `deploy` provisions templates into the project. To check available services/deployments use `railway service list` / `railway deployment list` instead. Deploying a private repo service that has no template requires the project's `railway config`/`.railway/railway.ts` deploy flow, not `railway deploy -t`.

## Verification Checklist

- [ ] CLI installed and accessible: `railway --version` returns version
- [ ] Shell PATH configured correctly
- [ ] Authentication complete: `railway projects list` shows projects
- [ ] Project linked: `railway status` shows project details
- [ ] Agent skills detected: `railway setup agent` reports configured tools
- [ ] Service status verified: `railway service list` shows service IDs and URLs

## References

- [Railway CLI Documentation](https://docs.railway.com/cli)
- [Railway Agent Setup](https://docs.railway.com/cli/setup)
- [GitHub CLI Repository](https://github.com/railwayapp/cli)
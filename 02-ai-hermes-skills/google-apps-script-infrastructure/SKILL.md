---
name: google-apps-script-infrastructure
category: deployment
description: Deploy Google Apps Script projects via infrastructure.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Google Apps Script, script.google, Apps Script, deployment]
    related_skills: [deployment, hermes-webui-deployment]
---

# Google Apps Script Infrastructure

## When to use
Use this skill when you need to **deploy and manage Google Apps Script projects** as part of your 01-core-infra infrastructure setup. This covers the `script.google` repository containing FollowUpReminder and LabelReminder scripts, as well as any other Google Apps Script projects.

**Common scenarios**:
- Setting up Google Apps Script scripts for email reminders and notifications
- Managing script.google repository deployment via GitHub
- Ensuring Google Apps Script scripts are properly configured for production
- Maintaining Google Apps Script infrastructure alongside other AI services

## Architecture Overview

Google Apps Script projects are **not traditional Docker containers** but are deployed via Google Cloud and accessed through the Google Apps Script API. This skill provides infrastructure for:

- Google Apps Script project deployment and management
- OAuth authentication for Google APIs
- Integration with other infrastructure components
- Monitoring and logging for script operations

## Infrastructure Components

### 1. Google Cloud Setup
- Google Cloud project creation for Apps Script deployment
- Apps Script API enablement
- OAuth 2.0 Desktop App credentials setup
- Service account management

### 2. Deployment Management
- `repos.manifest.jsonc` integration for Git repository management
- Branch management (main/upstream branches)
- Infrastructure separation (`infraSubdir: "."` for entire repo)
- Ansible-based idempotent deployment

### 3. Authentication & Security
- OAuth credentials storage (Ansible Vault or environment files)
- Service account key management
- API access control

### 4. Monitoring & Logging
- Google Cloud Logging integration
- Script execution monitoring
- Error tracking and alerting

## Common Commands

### Deployment via Ansible
```bash
# Run the main playbook
cd /home/aldo/dev/01-core-infra
cd ansible && ansible-playbook -i inventories/local.yml playbooks/site.yml
```

### Script Management
```bash
# Access Google Apps Script API
# Requires OAuth credentials setup
npx @google/clasp login
npx @google/clasp list
```

### Local Development
```bash
# For script.google repository
cd /home/aldo/dev/script-google
# Edit apps scripts in Google Apps Script editor
# Use clasp CLI to deploy changes
```

## Implementation Steps

### Phase 1: Repository Setup
1. **Update `repos.manifest.jsonc`** to include Google Apps Script repos:
   ```json
   {
     "name": "02-ai-script-google",
     "remote": "https://github.com/Aldo-f/script.google",
     "checkout": { "ref": "main", "type": "branch" },
     "infraSubdir": "."
   }
   ```

2. **Create infrastructure template** in `templates/apps/script-google/`:
   - `package.json` for Node.js tooling
   - `docker-compose.yml` for local development
   - `README.md` with deployment instructions

3. **Add systemd service** in `templates/systemd/02-ai-script-google.service`
   - For managing script operations
   - Include Google Apps Script environment variables

### Phase 2: Tool Sentry Setup
Add to `ansible/roles/tools/defaults/main.yml`:
```yaml
tools_sentries:
  ...
  script_google:
    command: "npm view @google/clasp version"
```

### Phase 3: Verification
After deployment, verify:
- Google Apps Script projects are accessible
- OAuth credentials are properly configured
- Scripts are running in the expected environment
- Integration with other infrastructure components

## Common Pitfalls

### 1. Authentication Issues
- **Problem**: Google Apps Script deployment requires OAuth credentials
- **Solution**: Store credentials securely in environment files or Ansible Vault
- **Best Practice**: Never commit credentials to git

### 2. Branch Management
- **Problem**: script.google uses multiple branches (main, upstream)
- **Solution**: Configure correct branch in repos.manifest.jsonc
- **Tip**: Use "upstream" branch for stable releases

### 3. Infrastructure Separation
- **Problem**: Apps Scripts are not traditional Docker containers
- **Solution**: Use Google Cloud infrastructure instead of Docker-based deployment
- **Note**: script.google scripts are managed via Apps Script API, not Docker

### 4. Environment Variables
- **Problem**: Hardcoded paths instead of using `__HOME__` macro
- **Solution**: Use `lookup('env', 'HOME')` in Ansible tasks with `become: false`
- **Tip**: Use `__HOME__` consistently across templates

## Integration with Other Components

### With 01-core-infra
- Part of the `02-ai` group in infrastructure taxonomy
- Deploys via `repos.manifest.jsonc` mechanism
- Integrated into existing Ansible deployment workflow

### With AI Services
- Complementary to other AI services (`02-ai-freellmapi`, `02-ai-llm-infra-sync`)
- Shares credential management patterns
- Uses same authentication infrastructure

### With Monitoring
- Can be monitored via existing infrastructure monitoring
- Logs go to Google Cloud Logging or local log files
- Integration with existing healthcheck systems

## Verification Commands

```bash
# Check if script.google is deployed
cd /home/aldo/dev
ls -la 02-ai-script-google/

# Verify Ansible deployment
cd /home/aldo/dev/01-core-infra
./install.sh

# Check Google Apps Script project status
# Requires proper OAuth setup
npx @google/clasp list
```

## References

- script.google repository: https://github.com/Aldo-f/script.google
- Google Apps Script documentation: https://developers.google.com/apps-script
- Clasp CLI: https://github.com/google/clasp

## Notes

This infrastructure template is designed to be **minimal and focused** because Google Apps Script projects are managed through Google Cloud APIs rather than traditional containerization. The template provides the scaffolding for proper deployment while keeping infrastructure complexity manageable.

The `script.google` repository specifically contains two production scripts:
- **FollowUpReminder**: Gmail reminder scripts for AWV dossier opvolging
- **LabelReminder**: Universal AI reminders via Gmail labels

Both scripts use advanced features like preview/dry-run modes, AI integrations, and comprehensive error handling.
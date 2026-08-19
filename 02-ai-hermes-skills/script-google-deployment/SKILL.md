---
name: script-google-deployment
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
description: Deploy script.google Google Apps Script projects.
tags:
  - deployment
  - Google Apps Script
  - automation
---

# Script.Google Deployment Setup

## When to use
Deploy the script.google repository containing FollowUpReminder and LabelReminder Google Apps Script projects as part of 01-core-infra infrastructure.

## Overview

This skill provides complete deployment of script.google projects, which contain:

- **FollowUpReminder** - Gmail reminder scripts for AWV dossier opvolging
- **LabelReminder** - Universal AI reminders via Gmail labels

**Key Insight**: Google Apps Script projects require Google Cloud infrastructure, not traditional Docker containers. They need OAuth authentication via the Apps Script API.

## Files Created

### Infrastructure Templates
- `templates/apps/script-google/package.json` - Node.js config
- `templates/apps/script-google/docker-compose.yml` - Local dev config
- `templates/apps/script-google/README.md` - App documentation

### Google Apps Script Templates
- `templates/infra/02-ai-script-google/README.md` - Infrastructure template
- `templates/systemd/02-ai-script-google.service` - Systemd service

### Scripts
- `scripts/check-google-auth.sh` - Verify OAuth setup
- `scripts/deploy-script-google.sh` - Deploy applications
- `scripts/validate-google-apps-script.sh` - Validate scripts

### Configuration
- `templates/infra/repos.manifest.jsonc` - Git repository manifest
- `ansible/roles/tools/defaults/main.yml` - Tool sentry (added `script_google`)

## Common Issues & Solutions

### 1. OAuth Setup
**Problem**: Google Apps Script requires OAuth credentials for deployment.
**Solution**: Store credentials in environment files, use `lookup('env', 'HOME')` in Ansible tasks.

### 2. Branch Management
**Problem**: script.google uses multiple branches (main, upstream).
**Solution**: Configure correct branch in repos.manifest.jsonc - use "upstream" for stable releases.

### 3. Infrastructure Separation
**Problem**: Apps Scripts are not traditional Docker containers.
**Solution**: Use Google Cloud infrastructure via Apps Script API.

### 4. Authentication Issues
**Problem**: OAuth authentication fails.
**Solution**: Store credentials securely, setup OAuth with `npx @google/clasp login`.

## Implementation

### Phase 1: Prerequisites
```bash
# Setup OAuth credentials
mkdir -p ~/.google-apps-script
cp credentials.json ~/.google-apps-script/
chmod 600 ~/.google-apps-script/credentials.json
```

### Phase 2: Infrastructure Setup
```bash
# Update repos.manifest.jsonc
templates/infra/repos.manifest.jsonc

# Setup tool sentry
ansible/roles/tools/defaults/main.yml
```

### Phase 3: Verification
```bash
# Check authentication
./scripts/check-google-auth.sh

# Deploy applications
./scripts/deploy-script-google.sh

# Validate scripts
./scripts/validate-google-apps-script.sh
```

## Key Patterns

### 1. Tool Sentry
Added `script_google` sentry to `ansible/roles/tools/defaults/main.yml`:
```yaml
script_google:
  command: "npm view @google/clasp version"
```

### 2. OAuth Integration
- Use `lookup('env', 'HOME')` instead of `ansible_env.HOME` for become contexts
- Store credentials in environment files
- Never commit credentials to git

### 3. Branch Management
```json
{
  "name": "02-ai-script-google",
  "remote": "https://github.com/Aldo-f/script.google",
  "checkout": { "ref": "upstream", "type": "branch" },
  "infraSubdir": "."
}
```

### 4. Verification Scripts
- `check-google-auth.sh` - Verify OAuth setup
- `validate-google-apps-script.sh` - Validate project integrity
- `deploy-script-google.sh` - Deploy applications

## References

- script.google repository: https://github.com/Aldo-f/script.google
- Google Apps Script documentation: https://developers.google.com/apps-script
- Clasp CLI: https://github.com/google/clasp

## Notes

This infrastructure setup follows established patterns:

1. **Ansible-based deployment**: Idempotent infrastructure setup via Ansible
2. **Git repository management**: Using repos.manifest.jsonc for managed repos
3. **OAuth authentication**: Secure credential management for Google APIs
4. **Verification and testing**: Comprehensive validation scripts

**Key Takeaway**: Google Apps Script projects require special infrastructure setup for authentication, deployment, and monitoring. This skill provides a complete, reusable solution for script.google deployment.

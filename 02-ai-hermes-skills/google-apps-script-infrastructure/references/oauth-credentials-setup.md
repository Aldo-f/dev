# Google Apps Script OAuth Credentials Setup

## Quick Reference

This document provides the essential setup instructions for configuring OAuth credentials for Google Apps Script projects in the script.google repository.

## Table of Contents

1. [Overview](#overview)
2. [Creating OAuth Credentials](#creating-oauth-credentials)
3. [Authentication Setup Script](#authentication-setup-script)
4. [Troubleshooting](#troubleshooting)
5. [Best Practices](#best-practices)

## Overview

Google Apps Script requires OAuth credentials for:

- **Deployment**: Using the `clasp` CLI to deploy scripts
- **Authentication**: Accessing Gmail API and other Google services
- **Authorization**: Managing triggers and executions

The script.google repository contains two Apps Script projects that need separate OAuth configurations:

- `FollowUpReminder` - AWV dossier opvolging
- `LabelReminder` - Universal AI reminders via labels

## Creating OAuth Credentials

### Step-by-Step Instructions

1. **Access Google Cloud Console**
   ```
   https://console.cloud.google.com
   ```

2. **Create or Select Project**
   - Choose existing project or create new one
   - Note the project ID (e.g., `script-google-prod`)

3. **Enable Google Apps Script API**
   ```bash
   gcloud services enable script.googleapis.com
   ```

4. **Create OAuth Client ID**
   - Navigate to: APIs & Services → Credentials
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Desktop app"
   - Add redirect URI: `http://localhost`
   - Click "Create"

5. **Download Credentials**
   - Credentials are shown on success page
   - Copy Client ID and Client Secret
   - Save to `~/.google-apps-script/credentials.json`

### Example Credentials File

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["http://localhost"]
  }
}
```

## Authentication Setup Script

### Complete Setup Script

```bash
#!/bin/bash
# setup-google-oauth.sh

CREDENTIALS_FILE="${CREDENTIALS_FILE:-~/.google-apps-script/credentials.json}"
CLASPrc_FILE="${CLASPrc_FILE:-~/.google-apps-script/.clasprc.json}"
PROJECT_BASE_DIR="${PROJECT_BASE_DIR:-~/dev/02-ai-script-google}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Check prerequisites
if ! command_exists npx; then
    echo "ERROR: npm/npx not found. Please install Node.js."
    exit 1
fi

if ! command_exists gcloud; then
    echo "ERROR: gcloud not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if credentials exist
if [[ ! -f "$CREDENTIALS_FILE" ]]; then
    echo "ERROR: Credentials file not found at $CREDENTIALS_FILE"
    echo "Please download OAuth credentials from Google Cloud Console"
    echo "and save them to $CREDENTIALS_FILE"
    exit 1
fi

# Create directory if it doesn't exist
mkdir -p "$(dirname "$CREDENTIALS_FILE")"
mkdir -p "$(dirname "$CLASPrc_FILE")"

# Verify credentials format
if ! grep -q '"client_id"' "$CREDENTIALS_FILE" || \
   ! grep -q '"client_secret"' "$CREDENTIALS_FILE" || \
   ! grep -q '"redirect_uris"' "$CREDENTIALS_FILE"; then
    echo "ERROR: Invalid credentials.json format"
    echo "Expected fields: client_id, client_secret, redirect_uris"
    exit 1
fi

log "Starting Google Apps Script OAuth setup..."

# Setup FollowUpReminder project
log "Setting up FollowUpReminder project..."
cd "$PROJECT_BASE_DIR/apps/FollowUpReminder" || {
    echo "ERROR: FollowUpReminder directory not found"
    echo "Run: mkdir -p $PROJECT_BASE_DIR/apps/FollowUpReminder"
    exit 1
}

# Remove existing configuration
rm -f .clasprc.json

# Login with custom credentials
npx @google/clasp login --creds "$CREDENTIALS_FILE" || {
    echo "ERROR: Failed to authenticate for FollowUpReminder"
    exit 1
}

# Create .clasp.json if it doesn't exist
if [[ ! -f ".clasp.json" ]]; then
    cat > .clasp.json << 'EOF'
{
  "projectId": "PLACEHOLDER_PROJECT_ID",
  "scriptId": "PLACEHOLDER_SCRIPT_ID",
  "rootDir": ".",
  "tokenPath": ".clasprc.json",
  "skipConsent": false
}
EOF
    echo "WARNING: Created .clasp.json with placeholder values"
    echo "Please update with actual project ID and script ID"
fi

# Setup LabelReminder project
log "Setting up LabelReminder project..."
cd "$PROJECT_BASE_DIR/apps/LabelReminder" || {
    echo "ERROR: LabelReminder directory not found"
    echo "Run: mkdir -p $PROJECT_BASE_DIR/apps/LabelReminder"
    exit 1
}

# Remove existing configuration
rm -f .clasprc.json

# Login with custom credentials
npx @google/clasp login --creds "$CREDENTIALS_FILE" || {
    echo "ERROR: Failed to authenticate for LabelReminder"
    exit 1
}

# Create .clasp.json if it doesn't exist
if [[ ! -f ".clasp.json" ]]; then
    cat > .clasp.json << 'EOF'
{
  "projectId": "PLACEHOLDER_PROJECT_ID",
  "scriptId": "PLACEHOLDER_SCRIPT_ID",
  "rootDir": ".",
  "tokenPath": ".clasprc.json",
  "skipConsent": false
}
EOF
    echo "WARNING: Created .clasp.json with placeholder values"
    echo "Please update with actual project ID and script ID"
fi

log "OAuth setup completed successfully!"
log "\nNext steps:"
log "1. Update .clasp.json files with correct project IDs"
log "2. Get actual script IDs from Google Apps Script dashboard"
log "3. Deploy scripts: npx @google/clasp push"
log "4. Set up triggers in appsscript.json"
log "5. Test authentication: npx @google/clasp list"
```

### Usage

Save the script and run:

```bash
chmod +x setup-google-oauth.sh
./setup-google-oauth.sh
```

## Troubleshooting

### Common Errors and Solutions

#### 1. "Consent Required" Error
**Problem**: User hasn't granted permissions to the app.

**Solution**:
```bash
rm ~/.google-apps-script/.clasprc.json
npx @google/clasp login --creds ~/.google-apps-script/credentials.json
```

#### 2. "Invalid Credentials" Error
**Problem**: Client ID or Client Secret is incorrect.

**Solution**:
```bash
# Check credentials file
nano ~/.google-apps-script/credentials.json

# Verify with Google Cloud Console
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Click on your OAuth client ID
# 3. Ensure it's active and not disabled
```

#### 3. "Redirect URI Mismatch" Error
**Problem**: Redirect URI doesn't match credentials.

**Solution**:
```bash
# Ensure credentials.json has:
"redirect_uris": ["http://localhost"]
```

#### 4. "Script Not Found" Error
**Problem**: Script ID is incorrect or script doesn't exist.

**Solution**:
```bash
# Get correct script ID:
npx @google/clasp list

# Update .clasp.json with correct script ID
```

#### 5. "Token Expired" Error
**Problem**: Access token has expired.

**Solution**:
```bash
# Re-authenticate
npx @google/clasp logout
npx @google/clasp login --creds ~/.google-apps-script/credentials.json
```

### Debug Commands

```bash
#!/bin/bash
# debug-google-oauth.sh

CLASPrc_FILE="~/.google-apps-script/.clasprc.json"

check_token() {
    if [[ -f "$CLASPrc_FILE" ]]; then
        echo "=== Token File Contents ==="
        cat "$CLASPrc_FILE"
        echo ""
    else
        echo "No token file found"
    fi
}

check_expiry() {
    if [[ -f "$CLASPrc_FILE" ]]; then
        echo "=== Token Expiry Check ==="
        # Extract expiry time from token (approximately 1 hour)
        # This is a simplified check - real tokens have JWT format
        echo "Token file exists but expiry check requires JWT parsing"
    fi
}

check_credentials_file() {
    CREDENTIALS_FILE="~/.google-apps-script/credentials.json"
    if [[ -f "$CREDENTIALS_FILE" ]]; then
        echo "=== Credentials File Info ==="
        echo "File size: $(stat -c %s "$CREDENTIALS_FILE") bytes"
        echo "Last modified: $(stat -c %y "$CREDENTIALS_FILE")"
        echo ""
        echo "=== Client ID ==="
        grep '"client_id"' "$CREDENTIALS_FILE" | head -1
        echo ""
        echo "=== Redirect URIs ==="
        grep '"redirect_uris"' "$CREDENTIALS_FILE" | head -1
    else
        echo "Credentials file not found"
    fi
}

check_token
check_expiry
check_credentials_file
```

## Best Practices

### 1. Security

```bash
# Set secure permissions
chmod 600 ~/.google-apps-script/credentials.json
chmod 700 ~/.google-apps-script

# Add to .gitignore
~/.google-apps-script/
.crecipes.json
```

### 2. Environment Variables

```bash
export GOOGLE_APPS_SCRIPT_CREDENTIALS="~/.google-apps-script/credentials.json"
export GOOGLE_APPS_SCRIPT_PROJECT_ID="script-google-prod"
```

### 3. Production Deployment

For production environments, use Ansible to manage credentials:

```yaml
- name: Setup Google Apps Script OAuth
  hosts: localhost
  become: false
  
  tasks:
    - name: Ensure credentials directory exists
      file:
        path: "{{ lookup('env', 'HOME') }}/.google-apps-script"
        state: directory
        mode: '0700'
      become: false
    
    - name: Copy production credentials
      copy:
        src: files/credentials.json
        dest: "{{ lookup('env', 'HOME') }}/.google-apps-script/credentials.json"
        mode: '0600'
      become: false
    
    - name: Setup authentication for FollowUpReminder
      command: |
        cd {{ lookup('env', 'HOME') }}/dev/02-ai-script-google/apps/FollowUpReminder
        npx @google/clasp login --creds ~/.google-apps-script/credentials.json
      become: false
    
    - name: Setup authentication for LabelReminder
      command: |
        cd {{ lookup('env', 'HOME') }}/dev/02-ai-script-google/apps/LabelReminder
        npx @google/clasp login --creds ~/.google-apps-script/credentials.json
      become: false
```

### 4. Credential Rotation

```bash
#!/bin/bash
# rotate-google-oauth.sh

CREDENTIALS_FILE="~/.google-apps-script/credentials.json"
BACKUP_DIR="~/.google-apps-script/backups"

# Create backup
mkdir -p "$BACKUP_DIR"
cp "$CREDENTIALS_FILE" "$BACKUP_DIR/credentials-$(date +%Y%m%d-%H%M%S).json"

# Generate new credentials (manual step)
echo "Please generate new OAuth credentials from Google Cloud Console"

# Update in application (example: update .clasp.json)
# This would be done based on your specific deployment method
```

## Integration with Existing Workflow

### 1. Add to Ansible Playbooks

```yaml
# In site.yml
roles:
  - google-apps-script

# Or as a task in an existing role
tasks:
  - include_role:
      name: google-apps-script
    when: inventory_hostname == 'localhost'
```

### 2. Cron Job for Credential Check

```bash
# Check credential health daily
0 2 * * * /path/to/check-google-auth-health.sh >> /var/log/google-apps-script-health.log 2>&1
```

### 3. Monitoring Integration

```yaml
# Add to existing monitoring setup
- name: Check Google Apps Script authentication
  shell: /path/to/check-google-auth-health.sh
  register: auth_check
  failed_when: auth_check.rc != 0
  tags: ['monitoring', 'google-apps-script']
```

## Quick Reference Commands

```bash
# Setup OAuth (one-time)
./setup-google-oauth.sh

# Check authentication health
./debug-google-oauth.sh

# Re-authenticate if needed
npx @google/clasp logout
npx @google/clasp login --creds ~/.google-apps-script/credentials.json

# List deployed scripts
npx @google/clasp list

# Deploy scripts
npx @google/clasp push
```

This comprehensive OAuth setup ensures secure and reliable access to Google Apps Script projects for the script.google repository.

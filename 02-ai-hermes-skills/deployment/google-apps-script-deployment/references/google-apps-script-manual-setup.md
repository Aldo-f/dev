# Google Apps Script Manual Setup Guide

## Google Cloud Console Configuration

### 1. Create/Select Google Cloud Project
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project or select existing: `script-google-prod`
- Enable **Google Apps Script API**

### 2. OAuth 2.0 Credentials
1. **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth Client ID**
3. Application type: **Desktop App**
4. Name: `script-google-clasp`
5. Authorized redirect URIs:
   - `http://192.168.0.5` (your server IP)
   - Do NOT use `localhost`
6. Save → Copy Client ID and Client Secret

### 3. OAuth Consent Screen
1. **APIs & Services** → **OAuth Consent Screen**
2. User Type: **External** (or Internal if using Workspace)
3. App Name: `Script Google Reminders`
4. Authorized domains: Add your domain if applicable
5. Test Users: Add your email(s) for testing

## Server-Side Setup (Raspberry Pi 5 / Headless)

### 1. Install clasp globally
```bash
sudo npm install -g @google/clasp
```

### 2. Configure credentials.json (optional)
```bash
mkdir -p ~/.config/clasp
cat > ~/.config/clasp/credentials.json << 'EOF'
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://192.168.0.5"]
  }
}
EOF
```

### 3. Authenticate clasp
```bash
# Global authentication (creates ~/.clasprc.json) using the custom credentials
clasp login --creds ~/.config/clasp/credentials.json

# Or use the automated helper script if you have placed your credentials under ~/scripts/google-workspace:
~/scripts/google-workspace/setup-clasp-creds.sh /path/to/downloaded_oauth_credentials.json
```

### 4. Verify authentication
```bash
clasp whoami
clasp list
```

## Reusable Helper Script: `setup-clasp-creds.sh`
To clean up clasp login actions and automate credentials mapping, drop this shell script into your global `~/scripts/google-workspace/` directory:

```bash
#!/bin/bash
# Reusable Setup Helper for Google Workspace OAuth Credentials
# Configures clasp to use a custom client ID and secret for local execution.

CREDS_JSON="$1"

if [ -z "$CREDS_JSON" ]; then
  echo "Usage: $0 /path/to/downloaded/oauth_credentials.json"
  exit 1
fi

if [ ! -f "$CREDS_JSON" ]; then
  echo "Error: Credentials file not found at '$CREDS_JSON'"
  exit 1
fi

clasp logout 2>/dev/null
clasp login --creds "$CREDS_JSON"
```

Make sure it's executable: `chmod +x ~/scripts/google-workspace/setup-clasp-creds.sh`.

## Complete Workspace Scopes (Full Control Setup)
If you want to configure a single, universal Google Client that can handle ALL possible workspace automation skills, add the following comprehensive scopes array to your `appsscript.json`:

```json
  "oauthScopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/keep.readonly",
    "https://www.googleapis.com/auth/contacts",
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/script.container.ui",
    "https://www.googleapis.com/auth/script.external_request",
    "https://www.googleapis.com/auth/script.deployments",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
  ]
```

## Deployment Scripts

### Project Structure
```
script.google/
├── FollowUpReminder/
│   ├── .clasp.json
│   ├── Code.gs
│   ├── Test.gs
│   └── appsscript.json
├── LabelReminder/
│   ├── .clasp.json
│   ├── Code.gs
│   ├── Test.gs
│   └── appsscript.json
├── shared/
│   └── AIProviders.gs
└── scripts/
    └── validate.js
```

### Push Commands
```bash
# From repo root
cd /home/aldo/dev/06-apps-script-google

# Validate all scripts
npm run validate

# Push FollowUpReminder
npm run push:followup

# Push LabelReminder
npm run push:label

# List deployed projects
clasp list
```

## Troubleshooting

### Common Errors

| Error | Solution |
|-------|----------|
| `Error retrieving access token` | Run `clasp login` again |
| `No credentials found` | Run `clasp login` |
| `redirect_uri_mismatch` | Add `http://192.168.0.5` to OAuth redirect URIs |
| `Permission denied` on global install | Use `sudo npm install -g @google/clasp` |
| `clasp: command not found` | Add npm global bin to PATH |

### Headless Server Notes
- The OAuth consent URL will contain a random port (e.g., `http://localhost:32945`)
- Open this URL in a browser from any machine on your LAN
- After authorization, clasp saves tokens to `~/.clasprc.json`
- Subsequent deployments use saved tokens (no browser needed)

## Security Best Practices
- Never commit `credentials.json` or `.clasprc.json` to git
- Add both to `.gitignore`
- Use Ansible Vault for server-side credential management
- Rotate OAuth credentials periodically
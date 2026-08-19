# Google Apps Script Infrastructure Setup

## Prerequisites

### Required Tools
Ensure the following tools are installed and available in PATH:

```bash
# Google Apps Script CLI
npm install -g @google/clasp

# Google Cloud SDK (optional, for deployment)
# curl https://sdk.cloud.google.com | bash
```

### OAuth Setup

1. Create a Google Cloud project:
   ```bash
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. Enable Google Apps Script API:
   ```bash
   gcloud services enable script.googleapis.com
   ```

3. Create OAuth Desktop App credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Add `http://localhost` as authorized redirect URI
   - Download the JSON credentials file

4. Store credentials locally:
   ```bash
   mkdir -p ~/.google-apps-script
   cp credentials.json ~/.google-apps-script/
   ```

### Environment Variables

Create a `.env` file for script.google deployment:

```env
GOOGLE_CLOUD_PROJECT_ID=script-google-prod
GOOGLE_APPS_SCRIPT_DEVELOPER_EMAIL=aldo@aldof.duckdns.org
GOOGLE_CLOUD_REGION=us-central1
NODE_ENV=production
```

## Initial Setup

### 1. Repository Structure

After the `02-ai-script-google` component is deployed:

```
/home/aldo/dev/
  02-ai-script-google/          # Cloned from https://github.com/Aldo-f/script.google
    apps/                       # Apps Script project files
    scripts/                    # Wrapper scripts
    .env                       # Environment variables (gitignore)
    .clasp.json                # Clasp configuration
```

### 2. Initial Authentication

```bash
# Navigate to the script.google repository
cd /home/aldo/dev/02-ai-script-google

# Login with Google OAuth
npx @google/clasp login --creds ~/.google-apps-script/credentials.json
```

### 3. Project Configuration

The script.google repository contains two Apps Script projects:

- **FollowUpReminder** - Gmail reminder scripts for AWV dossier opvolging
- **LabelReminder** - Universal AI reminders via Gmail labels

Both require separate OAuth configurations. Copy the credentials file and login for each project.

## Deployment Workflow

### 1. Script Preparation

```bash
# Clone the script.google repository (handled by Ansible)
# or ensure it's present in dev/02-ai-script-google/

# Check repository structure
ls -la apps/
```

### 2. Apps Script Deployment

```bash
# Deploy FollowUpReminder script
cd apps/FollowUpReminder
npx @google/clasp create --title "FollowUpReminder" --rootDir "."
npx @google/clasp push

# Deploy LabelReminder script  
cd ../LabelReminder
npx @google/clasp create --title "LabelReminder" --rootDir "."
npx @google/clasp push
```

### 3. Verification

```bash
# Check deployed scripts
npx @google/clasp list

# Test preview mode (for FollowUpReminder)
npx @google/clasp run previewReminders

# Test dry-run mode (for LabelReminder)
npx @google/clasp run dryRun
```

## Development Workflow

### Local Editing

1. Scripts are stored in the repository as Code.gs, Test.gs, and manifest files
2. Edit files directly in the repository
3. Push changes with:
   ```bash
   npx @google/clasp push
   ```

### Testing

```bash
# Run tests for FollowUpReminder
cd apps/FollowUpReminder
npx @google/clasp run testAll

# Run tests for LabelReminder
cd ../LabelReminder
npx @google/clasp run testAll
```

### Deployment for Production

1. Use non-dry-run functions to actually send emails:
   ```bash
   npx @google/clasp run checkReminders
   npx @google/clasp run checkDigests
   ```

2. Set `CREATE_DRAFTS = false` in config to send directly

## Troubleshooting

### Common Issues

**1. OAuth Authentication Fails**
```bash
# Remove cached credentials
rm ~/.google-apps-script/.clasprc.json
# Re-login
npx @google/clasp login --creds ~/.google-apps-script/credentials.json
```

**2. Script Not Deploying**
- Ensure you're in the correct project directory
- Check that .clasp.json is properly configured
- Verify internet connection for deployment

**3. Function Not Found**
- Apps Script projects are deployed separately
- Use `npx @google/clasp list` to verify both scripts are deployed
- Navigate to the correct project directory before running functions

**4. Timeout Issues**
- Apps Script has a 6-minute execution limit
- Scripts use batch processing to stay within limits
- Check execution logs in Google Apps Script dashboard

### Configuration Issues

**1. Environment Variables**
Ensure all required variables are set in the .env file:
```env
GOOGLE_CLOUD_PROJECT_ID=script-google-prod
GOOGLE_APPS_SCRIPT_DEVELOPER_EMAIL=aldo@aldof.duckdns.org
```

**2. Clasp Configuration**
Check `.clasp.json` for correct project ID and file configuration:

```json
{
  "projectId": "YOUR_PROJECT_NUMBER",
  "scriptId": "YOUR_SCRIPT_ID",
  "rootDir": ".",
  "tokenPath": ".clasprc.json"
}
```

**3. Apps Script Manifest**
Ensure `appsscript.json` is present and contains correct API scopes:

```json
{
  "timeZone": "Europe/Amsterdam",
  "runtimeVersion": "V8",
  "apis": [
    {
      "name": "Script",
      "version": "v1"
    },
    {
      "name": "Gmail",
      "version": "v1"
    }
  ],
  "trigger": [
    {
      "type": "ON_CE scheduled",
      "description": "Trigger every 6 hours",
      "parameters": {
        "time": "00 6,12,18 * * *"
      }
    }
  ]
}
```

## Monitoring

### 1. Google Apps Script Logs
- Monitor execution logs in Google Apps Script web interface
- Check for errors in the execution log for each script

### 2. Gmail Logs
- Scripts create drafts and send emails via Gmail API
- Monitor Gmail activity for delivery confirmation

### 3. Google Cloud Logging
- Enable logging for the Google Cloud project
- Monitor script execution logs and error logs

## Production Configuration

### 1. Cron Triggers
Apps Script uses time-based triggers for automatic execution:
- Every 6 hours for FollowUpReminder
- Every 6 hours for LabelReminder

### 2. Rate Limiting
- Scripts include rate limiting to avoid hitting API limits
- Use batch operations for large data sets

### 3. Error Handling
- All functions include error handling and logging
- Scripts continue execution even if individual operations fail
- Comprehensive test coverage for all critical functions

## Security Considerations

1. **Credentials Management**
   - Store OAuth credentials securely (never commit to git)
   - Use environment variables for sensitive data
   - Rotate credentials regularly

2. **API Access**
   - Limit API scopes to only what's necessary
   - Use service accounts where possible
   - Implement proper error handling for rate limits

3. **Data Handling**
   - Scripts access Gmail via API
   - Ensure proper data privacy and compliance
   - Implement data retention policies

## Next Steps

1. Complete initial OAuth setup
2. Deploy both script.google projects
3. Configure production environment
4. Set up monitoring and logging
5. Test in preview mode before production deployment

For more detailed information about specific Apps Script functionality, refer to the script.google repository documentation and the official Google Apps Script documentation.

# Google Apps Script Authentication Setup

## OAuth Configuration for script.google

### Prerequisites

Before setting up OAuth for Google Apps Script, you need:

1. A Google Cloud project
2. Google Apps Script API enabled
3. OAuth Desktop App credentials (Client ID + Client Secret)
4. A Google account with appropriate permissions

### Creating OAuth Desktop App Credentials

#### Step 1: Access Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select or create your project
3. Navigate to "APIs & Services" → "Credentials"

#### Step 2: Create OAuth Client ID
1. Click "Create Credentials" → "OAuth client ID"
2. For "Application type", select "Desktop app"
3. Add "http://localhost" to "Authorized redirect URIs"
4. Click "Create"

#### Step 3: Download Credentials
1. The credentials will be displayed on the next page
2. Copy the "Client ID" and "Client Secret"
3. Save them to a JSON file:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Authentication Setup Script

Create this script to automate OAuth setup:

```bash
#!/bin/bash
# setup-google-auth.sh

set -euo pipefail

CREDENTIALS_FILE="${CREDENTIALS_FILE:-~/.google-apps-script/credentials.json}"
CLASPRC_FILE="${CLASPRC_FILE:-~/.google-apps-script/.clasprc.json}"
PROJECTS=(
  "FollowUpReminder:AWV-dossier-opvolging"
  "LabelReminder:Universal-AI-reminders"
)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Check if credentials exist
if [[ ! -f "$CREDENTIALS_FILE" ]]; then
    echo "ERROR: Credentials file not found at $CREDENTIALS_FILE"
    echo "Please download OAuth credentials from Google Cloud Console"
    echo "and save them to $CREDENTIALS_FILE"
    exit 1
fi

# Create directory if it doesn't exist
mkdir -p "$(dirname "$CREDENTIALS_FILE")"
mkdir -p "$(dirname "$CLASPRC_FILE")"

log "Setting up Google Apps Script authentication..."

# Login for each project
for project_info in "${PROJECTS[@]}"; do
    IFS=':' read -r project_name description <<< "$project_info"
    
    echo "\n=== Setting up $project_name ==="
    echo "Description: $description"
    
    # Remove existing clasp configuration
    rm -f "$CLASPrc_FILE"
    
    # Login with custom credentials
    cd "apps/$project_name" || {
        echo "ERROR: Directory apps/$project_name not found"
        continue
    }
    
    npx @google/clasp login --creds "$CREDENTIALS_FILE" || {
        echo "ERROR: Failed to login for $project_name"
        continue
    }
    
    # Create script if it doesn't exist
    if [[ ! -f "appsscript.json" ]]; then
        echo "Creating appsscript.json for $project_name..."
        # Create basic appsscript.json
        cat > appsscript.json << 'EOF'
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
  "trigger": []
}
EOF
    fi
    
    # Create .clasp.json if it doesn't exist
    if [[ ! -f ".clasp.json" ]]; then
        echo "Creating .clasp.json for $project_name..."
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
    
    echo "✓ $project_name authentication setup completed"
    cd - > /dev/null

done

log "Authentication setup completed successfully!"
log "\nNext steps:"
log "1. Update .clasp.json files with correct project IDs"
log "2. Deploy scripts with: npx @google/clasp push"
log "3. Configure triggers in appsscript.json"
log "4. Test authentication with: npx @google/clasp list"
```

### OAuth Best Practices

1. **Never commit credentials to git**
   ```bash
   echo "credentials.json" >> .gitignore
   echo ".clasprc.json" >> .gitignore
   ```

2. **Use environment variables for sensitive data**
   ```bash
   export GOOGLE_APPS_SCRIPT_CREDENTIALS="~/.google-apps-script/credentials.json"
   ```

3. **Secure credential storage**
   - Store credentials in a secure location
   - Use file permissions: `chmod 600 ~/.google-apps-script/credentials.json`
   - Consider using Ansible Vault or HashiCorp Vault for production

### Troubleshooting

#### 1. "Consent Required" Error
```bash
# Force re-authentication
rm ~/.google-apps-script/.clasprc.json
npx @google/clasp login --creds ~/.google-apps-script/credentials.json
```

#### 2. "Invalid Credentials" Error
```bash
# Check if credentials are correct
nano ~/.google-apps-script/credentials.json
# Verify client_id and client_secret are valid
```

#### 3. "Redirect URI Mismatch" Error
```bash
# Ensure credentials.json has:
"redirect_uris": ["http://localhost"]
```

#### 4. "Script Not Found" Error
```bash
# Check if script exists in Google Apps Script dashboard
# and that .clasp.json has correct scriptId
npx @google/clasp list
```

### Integration with Ansible

For production deployments, integrate OAuth setup into your Ansible playbook:

```yaml
- name: Setup Google Apps Script authentication
  block:
    - name: Ensure credentials directory exists
      file:
        path: "{{ lookup('env', 'HOME') }}/.google-apps-script"
        state: directory
        mode: '0700'
      become: false

    - name: Copy OAuth credentials
      copy:
        src: files/credentials.json
        dest: "{{ lookup('env', 'HOME') }}/.google-apps-script/credentials.json"
        mode: '0600'
      become: false

    - name: Setup clasp configuration
      template:
        src: .clasp.json.j2
        dest: "{{ lookup('env', 'HOME') }}/dev/02-ai-script-google/apps/FollowUpReminder/.clasp.json"
        mode: '0644'
      become: false

    - name: Setup clasp configuration for LabelReminder
      template:
        src: .clasp.json.j2
        dest: "{{ lookup('env', 'HOME') }}/dev/02-ai-script-google/apps/LabelReminder/.clasp.json"
        mode: '0644'
      become: false
  tags: ['google-apps-script', 'oauth']
```

### Monitoring OAuth Health

```bash
#!/bin/bash
# check-google-auth-health.sh

CREDENTIALS_FILE="~/.google-apps-script/credentials.json"
CLASPrc_FILE="~/.google-apps-script/.clasprc.json"

check_credentials() {
    if [[ ! -f "$CREDENTIALS_FILE" ]]; then
        echo "ERROR: Credentials file not found"
        return 1
    fi
    
    if [[ $(stat -c %a "$CREDENTIALS_FILE") != "600" ]]; then
        echo "WARNING: Credentials file permissions too open"
    fi
    
    if ! grep -q '"client_id"' "$CREDENTIALS_FILE"; then
        echo "ERROR: Invalid credentials format"
        return 1
    fi
}

check_clasprc() {
    if [[ ! -f "$CLASPrc_FILE" ]]; then
        echo "WARNING: .clasprc.json not found (may need login)"
        return 1
    fi
    
    if ! grep -q '"access_token"' "$CLASPrc_FILE"; then
        echo "WARNING: No access token found"
        return 1
    fi
}

check_credentials
check_clasprc

echo "✓ OAuth health check completed"
```

This authentication setup ensures secure and reliable access to Google Apps Script projects for the script.google repository.

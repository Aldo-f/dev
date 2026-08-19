# 06-apps-scripts-google infrastructure template
# Beheerd door 01-core-infra install.sh
# Wijzig ALLEEN via templates/infra/06-apps-scripts-google/

# Google Apps Script (script.google) is a Google Workspace integration project
# containing FollowUpReminder and LabelReminder scripts. This template provides
# Google Cloud infrastructure for the Apps Script deployment and management.

# Required dependencies for Google Apps Script deployment
# Install sentry for @google/clasp in ansible/roles/tools/defaults/main.yml:
# script_google:
#   command: "npm view @google/clasp version"

# Infrastructure components needed for script.google:

# 1. Google Cloud Project Setup
# - Create a Google Cloud project for Apps Script deployment
# - Enable the Apps Script API
# - Set up OAuth 2.0 Desktop App credentials
# - Add authorized redirect URI: http://192.168.0.5 (server IP, NOT localhost)

# 2. Environment Variables
# .env.template for script.google deployment
GOOGLE_CLOUD_PROJECT_ID=script-google-prod
GOOGLE_APPS_SCRIPT_DEVELOPER_EMAIL=aldo@aldof.duckdns.org
GOOGLE_CLOUD_REGION=us-central1
CLASP_REDIRECT_URI=http://192.168.0.5

# 3. Deployment Configuration
DEPLOY_ENVIRONMENT=production
APPS_SCRIPT_TIMEOUT=180

# 4. Monitoring & Logging
GOOGLE_APPS_SCRIPT_LOGGING_ENABLED=true
CLOUD_LOGGING_PROJECT=script-google-logging

# 5. Security
# Store OAuth credentials in Ansible Vault or environment files
# Never commit credentials to git
# Global clasp credentials stored in ~/.clasprc.json (per user)

# Deployment workflow (manual, not automated):
# 1. git clone https://github.com/Aldo-f/script.google
# 2. cd script.google
# 3. npm install
# 4. sudo npm install -g @google/clasp
# 5. npm run login  # Opens browser for OAuth, saves to ~/.clasprc.json
# 6. npm run validate
# 7. npm run push:followup && npm run push:label

# This template is minimal because script.google primarily depends on
# Google Cloud Platform infrastructure rather than traditional Docker containers.
# The actual deployment happens via Google Apps Script API using clasp.

# Files to be created in scripts/:
# - npm install @google/clasp
# - npx clasp login
# - npx clasp create --title "script.google" --rootDir "."
# - npx clasp push

# Additional configuration for Google Apps Script
dir
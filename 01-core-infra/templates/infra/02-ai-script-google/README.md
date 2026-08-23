# 02-ai-script-google infrastructure template
# Beheerd door 01-core-infra install.sh
# Wijzig ALLEEN via templates/infra/02-ai-script-google/

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

# 2. Environment Variables
# .env.template for script.google deployment
GOOGLE_CLOUD_PROJECT_ID=script-google-prod
GOOGLE_APPS_SCRIPT_DEVELOPER_EMAIL=aldo@aldof.duckdns.org
GOOGLE_CLOUD_REGION=us-central1

# 3. Deployment Configuration
DEPLOY_ENVIRONMENT=production
APPS_SCRIPT_TIMEOUT=180

# 4. Monitoring & Logging
GOOGLE_APPS_SCRIPT_LOGGING_ENABLED=true
CLOUD_LOGGING_PROJECT=script-google-logging

# 5. Security
# Store OAuth credentials in Ansible Vault or environment files
# Never commit credentials to git

# Example Dockerfile for wrapper scripts
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --only=production
COPY . .
EXPOSE 3000
CMD ["node", "src/index.js"]

# Example docker-compose.yml for local development
version: "3.9"
services:
  script-google-app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - GOOGLE_CLOUD_PROJECT_ID=${GOOGLE_CLOUD_PROJECT_ID}
      - GOOGLE_APPS_SCRIPT_DEVELOPER_EMAIL=${GOOGLE_APPS_SCRIPT_DEVELOPER_EMAIL}
      - NODE_ENV=${DEPLOY_ENVIRONMENT}
    volumes:
      - ./src:/app/src
    restart: unless-stopped
    networks:
      - traefik_net

networks:
  traefik_net:
    external: true

# This template is minimal because script.google primarily depends on
# Google Cloud Platform infrastructure rather than traditional Docker containers.
# The actual deployment happens via Google Apps Script API using clasp.

# Files to be created in scripts/:- npm install @google/clasp- npx clasp login- npx clasp create --title "script.google" --rootDir "."- npx clasp push

# Files to be created in scripts/:- npm install @google/clasp- npx clasp login- npx clasp create --title "script.google" --rootDir "."- npx clasp push

# Additional configuration for Google Apps Script
dir

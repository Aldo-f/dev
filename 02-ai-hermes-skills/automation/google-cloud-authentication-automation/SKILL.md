---
name: google-cloud-authentication-automation
authors:
  - aldo
created: 2026-07-31
updated: 2026-07-31
skill_tag: automation devops
description: Automate ADC setup and testing for Google Cloud services.
---

# Google Cloud Authentication Automation

**Goal:** Automate Application Default Credentials (ADC) setup, validation, and testing for Google Cloud services across development, testing, and production environments.

## Overview

This skill provides a comprehensive framework for setting up, testing, and maintaining Google Cloud authentication using Application Default Credentials (ADC). It covers credential file creation, validation testing, integration with infrastructure tools, and automated verification for reliable Google Cloud service access.

## When to Use

Use this skill when you need to:

- Set up Application Default Credentials for Google Cloud services
- Automate credential testing and validation
- Integrate ADC setup with Ansible infrastructure
- Create reusable credential setup scripts for teams
- Validate credential structure and accessibility
- Test Google Cloud service connectivity with ADC

## Core Workflow

### 1. Credential File Setup

```bash
setup_adc.sh [PROJECT_ID] [SERVICE_ACCOUNT_EMAIL] [KEY_FILE]
```

**Parameters:**
- `PROJECT_ID`: Google Cloud project ID (defaults to `my-demo-project`)
- `SERVICE_ACCOUNT_EMAIL`: Service account email (auto-generated if not provided)
- `KEY_FILE`: Path to service account key file (defaults to `/tmp/service-account-key.json`)

**What it does:**
- Creates a service account key file with proper JSON structure
- Sets `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Sources Google Cloud SDK path for CLI commands
- Configures project settings

### 2. Credential Validation

```bash
test_adc.py
```

**What it validates:**
- Google Cloud SDK availability and configuration
- Authentication account setup
- Project access and permissions
- GOOGLE_APPLICATION_CREDENTIALS file structure
- Required service account fields

### 3. Integration with Infrastructure

```bash
# Add to Ansible roles/tools/defaults/main.yml
gcloud:
  command: "gcloud --version"
```

**Ensures:**
- Google Cloud SDK is included in tool sentry checks
- Infrastructure deployment includes necessary authentication tools
- Consistent credential setup across environments

## Key Components

### setup_adc.sh

**Purpose:** Complete ADC setup automation script

**Features:**
- Creates service account key files with proper structure
- Sets up environment variables for ADC
- Integrates with Google Cloud SDK
- Includes comprehensive error handling
- Provides detailed output and verification

**Usage:**
```bash
# Basic usage
cd /home/aldo
./setup_adc.sh

# Custom parameters
./setup_adc.sh my-production-project dev@mycompany.com /path/to/key.json
```

### test_adc.py

**Purpose:** Automated ADC validation and testing

**Validation Areas:**
- Google Cloud SDK command availability
- Project configuration verification
- Authentication account status
- Service account file validation
- Storage service connectivity (optional)

**Output:**
- Clear pass/fail status for each test
- Detailed error messages for debugging
- Success confirmation when setup is complete

## Pitfalls and Best Practices

### Common Issues

1. **Missing Google Cloud SDK**
   - **Fix:** Use `setup_adc.sh` which sources SDK automatically
   - **Prevention:** Add gcloud sentry to Ansible tool checks

2. **Invalid Credential File Structure**
   - **Fix:** Use the JSON structure provided in `setup_adc.sh`
   - **Prevention:** `test_adc.py` validates required fields

3. **Authentication Not Loaded**
   - **Fix:** Run `gcloud auth application-default login` for interactive auth
   - **Prevention:** Scripts include validation and error handling

### Environment-Specific Considerations

- **Development:** Use service account keys with limited permissions
- **Testing:** Mock or test credentials in CI/CD pipelines
- **Production:** Use managed service accounts with proper IAM roles

## Integration with Infrastructure

### Ansible Integration

```yaml
# ansible/roles/tools/defaults/main.yml
tools_sentries:
  # ... other tools ...
  gcloud:
    command: "gcloud --version"
```

### Cron Job Integration

```yaml
# templates/cron/google-cloud-auth.cron
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/bin

# Daily ADC validation at 2 AM
0 2 * * * aldo cd /home/aldo && ./test_adc.py >/var/log/google-cloud-auth-validation.log 2>&1
```

## Advanced Usage

### Custom Credential Files

Replace the generated key file with your actual service account JSON:

```bash
cat > /path/to/your-key.json << 'EOF'
{
  "type": "service_account",
  "project_id": "your-project",
  "private_key_id": "your-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
EOF

export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
```

### CI/CD Integration

```yaml
# .github/workflows/google-cloud.yml
name: Google Cloud Authentication Setup

on:
  push:
    paths:
      - 'setup_adc.sh'
      - 'test_adc.py'

jobs:
  test-adc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Google Cloud SDK
        run: gcloud --version || echo "gcloud not available"
      - name: Test ADC Setup
        run: python3 test_adc.py
```

## Troubleshooting

### ADC Not Working

```bash
# Check if credentials are set
echo $GOOGLE_APPLICATION_CREDENTIALS

# List authenticated accounts
gcloud auth list

# Verify project configuration
gcloud config list core/project
```

### Python Module Issues

```bash
# Install required Python modules
pip install google-cloud-storage

# Or use virtual environment
python3 -m venv adc_test_venv
source adc_test_venv/bin/activate
pip install google-cloud-storage
```

### Ansible Tool Issues

```bash
# Ensure tools sentry is present
ansible-playbook -i inventories/local.yml playbooks/site.yml

# Manually check for Google Cloud SDK
command -v gcloud || echo "gcloud not found"
```

## Maintenance and Updates

### Regular Validation

Run this script weekly to ensure ADC setup remains valid:

```bash
#!/bin/bash
cd /home/aldo
./test_adc.py > adc_validation.log 2>&1

if [ $? -eq 0 ]; then
    echo "ADC validation passed"
else
    echo "ADC validation failed - investigate log"
    exit 1
fi
```

### Credential Rotation

When service account keys need rotation:

1. Generate new key from Google Cloud Console
2. Replace `GOOGLE_APPLICATION_CREDENTIALS` file
3. Run `setup_adc.sh` with new parameters
4. Validate with `test_adc.py`

## Examples

### Example 1: Basic Setup

```bash
# Simple setup with default parameters
cd /home/aldo
./setup_adc.sh
```

### Example 2: Production Setup

```bash
# Production-grade setup
cd /home/aldo
./setup_adc.sh production-project prod@company.com /secrets/production-key.json
```

### Example 3: Interactive Testing

```bash
# Test credential setup
cd /home/aldo
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/existing-key.json"
python3 test_adc.py
```

## References

- [Google Cloud ADC Documentation](https://cloud.google.com/docs/authentication/external/set-up-adc)
- [Google Cloud SDK Installation](https://cloud.google.com/sdk/docs/install)
- [Service Account JSON Structure](https://cloud.google.com/iam/docs/creating-managing-service-accounts#key)

## Configuration

### Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file
- `PROJECT_ID`: Google Cloud project ID
- `SERVICE_ACCOUNT_EMAIL`: Service account email address

### File Locations

- `setup_adc.sh`: `/home/aldo/setup_adc.sh`
- `test_adc.py`: `/home/aldo/test_adc.py`
- Ansible config: `/dev/01-core-infra/ansible/roles/tools/defaults/main.yml`

This skill provides a complete, production-ready framework for Google Cloud authentication automation that can be used across development teams and integrated with existing infrastructure pipelines.
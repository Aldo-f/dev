---
name: ansible-credential-management
description: "Manage sensitive credentials via Ansible Vault for Hermes"
version: 1.0.0
author: Hermes Agent + Nous Research
license: MIT
platforms: [linux]
tags: [ansible, credentials, vault, deployment, security]
---
# Ansible Credential Management for Hermes

## Core Principle
Never store plaintext secrets in runtime files or git repositories. Use Ansible Vault for encryption and template-based injection for runtime use.

## When to Use This Skill
Use when you need to manage sensitive credentials (API keys, tokens) for Hermes or applications in a secure, production-ready way that prevents accidental secret exposure.

## Directory Structure
```
~/dev/01-core-infra/
  └── vaults/
      └── hermes-credentials.yml   # Encrypted vault file (never commit)
  └── ansible/
      └── templates/
          └── infra/hermes/
              └── auth.json.j2        # Template for auth.json
      └── roles/
          └── templates/
              └── tasks/main.yml      # Deployment task
```

## Implementation Steps

### 1. Create Encrypted Vault File
```bash
ansible-vault create dev/01-core-infra/vaults/hermes-credentials.yml
```

### 2. Define Credential Variables
Create credential variables with safe naming:
```yaml
vault_{provider}_{cred_id}: "actual-value"
```

Example:
```yaml
hermes_credential_pool:
  openrouter:
    - id: "503f6e"
      label: "OPENROUTER_API_KEY"
      auth_type: "api_key"
      priority: 0
      source: "env:OPENROUTER_API_KEY"
      access_token: "{{ vault_openrouter_503f6e }}"
      base_url: "https://openrouter.ai/api/v1"
      secret_fingerprint: "sha256:8c0b81d00065aa52"
```

### 3. Template File (auth.json.j2)
Generate the final `~/.hermes/auth.json` from your credentials:

```jinja2
{
  "version": 1,
  "providers": {},
  "active_provider": null,
  "updated_at": "{{ ansible_date_time.iso8601 }}",
  "credential_pool": {
    "openrouter": [
      {
        "id": "503f6e",
        "label": "OPENROUTER_API_KEY",
        "auth_type": "api_key",
        "priority": 0,
        "source": "env:OPENROUTER_API_KEY",
        "access_token": "{{ vault_openrouter_503f6e }}",
        "last_status": null,
        "last_status_at": null,
        "last_error_code": null,
        "last_error_reason": null,
        "last_error_message": null,
        "last_error_reset_at": null,
        "base_url": "https://openrouter.ai/api/v1",
        "request_count": 0,
        "secret_fingerprint": "sha256:8c0b81d00065aa52"
      },
      {
        "id": "52f84e",
        "label": "api-key-6",
        "auth_type": "api_key",
        "priority": 0,
        "source": "manual",
        "access_token": "{{ vault_opencode_zen_52f84e }}",
        "last_status": "ok",
        "last_status_at": null,
        "last_error_code": null,
        "last_error_reason": null,
        "last_error_message": null,
        "last_error_reset_at": null,
        "base_url": "https://opencode.ai/zen/v1",
        "request_count": 2
      }
    ]
  }
}
```

### 4. Deploy Task Example
```yaml
- name: Deploy Hermes credentials template
  copy:
    src: "{{ playbook_dir }}/templates/infra/hermes/auth.json.j2"
    dest: "{{ ansible_hermes_home }}/auth.json"
    owner: aldo
    group: aldo
    mode: "0600"
  notify: Reload Hermes
  no_log: true
  vars_files:
    - "{{ playbook_dir }}/vaults/hermes-credentials.yml"
```

### 5. Deploy with Vault Password
```bash
ansible-playbook -i inventories/local.yml playbooks/site.yml --ask-vault-pass
```

## Per-App .env Rendering (freellmapi pattern)

For apps whose runtime `.env` is gitignored and can be wiped by repo syncs, render it from vault on every deploy:

1. Vault file per app: `vaults/freellmapi-credentials.yml` with `vault_<app>_<var>` keys (encrypt with `ansible-vault encrypt --vault-password-file vaults/master.key`).
2. Template: `templates/infra/02-ai-freellmapi/infra/.env.j2` (jinja vars, e.g. `ENCRYPTION_KEY={{ vault_freellmapi_encryption_key }}`).
3. Task before `docker-compose up`:
```yaml
- name: Load app vault credentials
  include_vars:
    file: "{{ lookup('env', 'HOME') }}/dev/01-core-infra/vaults/freellmapi-credentials.yml"
  no_log: true
- name: Render app .env from vault
  template:
    src: "{{ template_dir }}/infra/02-ai-freellmapi/infra/.env.j2"
    dest: /home/aldo/dev/02-ai-freellm/.env
    owner: aldo
    group: aldo
    mode: "0600"
  no_log: true
```
4. `ansible.cfg`: `vault_password_file = /home/aldo/dev/01-core-infra/vaults/master.key` (absolute path).

Pitfalls:
- Use `lookup('env', 'HOME')`, NOT `ansible_env.HOME`, for the vault path in `become: true` contexts (`ansible_env.HOME` resolves to `/root`).
- A file named `master.key` may itself be a vault-encrypted blob (AES256, not a plaintext password) — check with `file`. If so it cannot be used as `--vault-password-file`; create a plaintext key with `openssl rand -base64 32`.
- Keep the plaintext key out of git; the ENCRYPTED vault file is safe to commit (standard practice) and doubles as backup.

## Recovering a lost .env
When a gitignored `.env` vanishes (git pull / reset / clean), the running
container is a full snapshot of its values if compose used `env_file: .env`:
`docker inspect <container> --format '{{json .Config.Env}}'`. Full recovery
recipe, ENCRYPTION_KEY notes, and gitignore-negation pitfalls:
references/recovering-lost-env.md.

## Security Best Practices
- Use `ansible-vault encrypt` for all secret files
- Never commit vault files or decrypted credentials to git
- Use strong, complex vault passwords (20+ characters)
- Restrict vault access to deployment systems only
- Never commit runtime credential files

## GitHub Actions Automated Credential Sync

When you need credentials refreshed automatically on every commit or on a nightly schedule:

```yaml
# .github/workflows/hermes-credential-sync.yml
on:
  push:
    branches: [main, develop]
    paths:
      - 'dev/01-core-infra/vaults/hermes-credentials.yml'
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC for backup
  workflow_dispatch:
    inputs:
      force_sync:
        description: 'Force credential sync even if no changes'
        required: false
        default: false
        type: boolean

env:
  ANSIBLE_VAULT_MASTER_KEY: ${{ secrets.ANSIBLE_VAULT_MASTER_KEY }}
  MASTER_CREDENTIALS_ENCRYPTED: ${{ secrets.MASTER_CREDENTIALS_ENCRYPTED }}

jobs:
  credential-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.9' }
      - run: pip3 install ansible
      # Decode master payload from Base64, decrypt via vault, deploy
      - name: Decrypt and deploy credentials
        env:
          MASTER_CREDENTIALS: ${{ secrets.MASTER_CREDENTIALS_ENCRYPTED }}
        run: |
          echo "$(echo $MASTER_CREDENTIALS | base64 -d)" > vaults/hermes-credentials.yml
          ansible-vault encrypt vaults/hermes-credentials.yml \
            --vault-password-file <(echo "$ANSIBLE_VAULT_MASTER_KEY")
          ansible-playbook playbooks/site.yml --ask-vault-pass
      # Validate generated auth.json
      - name: Validate auth.json
        run: |
          python3 -c "
          import json
          d = json.load(open('$HOME/.hermes/auth.json'))
          assert d.get('version') == 1
          assert 'credential_pool' in d
          print(f'OK: {sum(len(v) for v in d[\"credential_pool\"].values())} credentials')
          "
      # Nightly backup uploads
      - uses: actions/upload-artifact@v3
        with:
          name: credentials-backup
          path: credentials_backup_*.json
          retention-days: 7
```

### Setup Steps for GitHub Actions
1. Generate master key: `openssl rand -base64 32 | tr -d '/+=' > vaults/master.key`
2. Encrypt credentials: `ansible-vault encrypt vaults/hermes-credentials.yml --vault-password-file vaults/master.key`
3. Add GitHub Secrets:
   - `ANSIBLE_VAULT_MASTER_KEY` — the password from step 1
   - `MASTER_CREDENTIALS_ENCRYPTED` — Base64-encoded full credential payload: `cat vaults/hermes-credentials.yml | base64 -w 0`
4. Add `vaults/master.key` to `.gitignore` so they are never committed

## Supporting Files
- `templates/github-actions-credential-sync.yml` - GitHub Actions workflow for automated sync
- `references/security-patterns.md` - Security reference and emergency recovery procedures
- `references/recovering-lost-env.md` - Guide to recovering lost .env files from running containers or backups
## Security Best Practices
- Use `ansible-vault encrypt` for all secret files
- Never commit vault files or decrypted credentials to git
- Use strong, complex vault passwords (20+ characters)
- Restrict vault access to deployment systems only
- Never commit runtime credential files

## GitHub Actions Automated Credential Sync (NEW)

When you need credentials refreshed automatically on every commit or on a nightly schedule:

```yaml
# .github/workflows/hermes-credential-sync.yml
on:
  push:
    branches: [main, develop]
    paths:
      - 'dev/01-core-infra/vaults/hermes-credentials.yml'
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC for backup
  workflow_dispatch:
    inputs:
      force_sync:
        description: 'Force credential sync even if no changes'
        required: false
        default: false
        type: boolean

env:
  ANSIBLE_VAULT_MASTER_KEY: ${{ secrets.ANSIBLE_VAULT_MASTER_KEY }}
  MASTER_CREDENTIALS_ENCRYPTED: ${{ secrets.MASTER_CREDENTIALS_ENCRYPTED }}

jobs:
  credential-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.9' }
      - run: pip3 install ansible
      # Decode master payload from Base64, decrypt via vault, deploy
      - name: Decrypt and deploy credentials
        env:
          MASTER_CREDENTIALS: ${{ secrets.MASTER_CREDENTIALS_ENCRYPTED }}
        run: |
          echo "$(echo $MASTER_CREDENTIALS | base64 -d)" > vaults/hermes-credentials.yml
          ansible-vault encrypt vaults/hermes-credentials.yml \
            --vault-password-file <(echo "$ANSIBLE_VAULT_MASTER_KEY")
          ansible-playbook playbooks/site.yml --ask-vault-pass
      # Validate generated auth.json
      - name: Validate auth.json
        run: |
          python3 -c "
          import json
          d = json.load(open('$HOME/.hermes/auth.json'))
          assert d.get('version') == 1
          assert 'credential_pool' in d
          print(f'OK: {sum(len(v) for v in d[\"credential_pool\"].values())} credentials')
          "
      # Nightly backup uploads
      - uses: actions/upload-artifact@v3
        with:
          name: credentials-backup
          path: credentials_backup_*.json
          retention-days: 7
```

### Setup Steps for GitHub Actions
1. Generate master key: `openssl rand -base64 32 | tr -d '/+=' > vaults/master.key`
2. Encrypt credentials: `ansible-vault encrypt vaults/hermes-credentials.yml --vault-password-file vaults/master.key`
3. Add GitHub Secrets:
   - `ANSIBLE_VAULT_MASTER_KEY` — the password from step 1
   - `MASTER_CREDENTIALS_ENCRYPTED` — Base64-encoded full credential payload: `cat vaults/hermes-credentials.yml | base64 -w 0`
4. Add `vaults/master.key` and `.env` to `.gitignore` so they are never committed

## GitHub Actions Automated Credential Sync (NEW)

When you need credentials refreshed automatically on every commit or on a nightly schedule:

```yaml
# .github/workflows/hermes-credential-sync.yml
on:
  push:
    branches: [main, develop]
    paths:
      - 'dev/01-core-infra/vaults/hermes-credentials.yml'
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC for backup
  workflow_dispatch:
    inputs:
      force_sync:
        description: 'Force credential sync even if no changes'
        required: false
        default: false
        type: boolean

env:
  ANSIBLE_VAULT_MASTER_KEY: ${{ secrets.ANSIBLE_VAULT_MASTER_KEY }}
  MASTER_CREDENTIALS_ENCRYPTED: ${{ secrets.MASTER_CREDENTIALS_ENCRYPTED }}

jobs:
  credential-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.9' }
      - run: pip3 install ansible
      # Decode master payload from Base64, decrypt via vault, deploy
      - name: Decrypt and deploy credentials
        env:
          MASTER_CREDENTIALS: ${{ secrets.MASTER_CREDENTIALS_ENCRYPTED }}
        run: |
          echo "$(echo $MASTER_CREDENTIALS | base64 -d)" > vaults/hermes-credentials.yml
          ansible-vault encrypt vaults/hermes-credentials.yml \
            --vault-password-file <(echo "$ANSIBLE_VAULT_MASTER_KEY")
          ansible-playbook playbooks/site.yml --ask-vault-pass
      # Validate generated auth.json
      - name: Validate auth.json
        run: |
          python3 -c "
          import json
          d = json.load(open('$HOME/.hermes/auth.json'))
          assert d.get('version') == 1
          assert 'credential_pool' in d
          print(f'OK: {sum(len(v) for v in d[\"credential_pool\"].values())} credentials')
          "
      # Nightly backup uploads
      - uses: actions/upload-artifact@v3
        with:
          name: credentials-backup
          path: credentials_backup_*.json
          retention-days: 7
```

### Setup Steps for GitHub Actions
1. Generate master key: `openssl rand -base64 32 | tr -d '/+=' > vaults/master.key`
2. Encrypt credentials: `ansible-vault encrypt vaults/hermes-credentials.yml --vault-password-file vaults/master.key`
3. Add GitHub Secrets:
   - `ANSIBLE_VAULT_MASTER_KEY` — the password from step 1
   - `MASTER_CREDENTIALS_ENCRYPTED` — Base64-encoded full credential payload: `cat vaults/hermes-credentials.yml | base64 -w 0`
4. Add `vaults/master.key` and `.env` to `.gitignore` so they are never committed

## Verification Steps
1. Validate JSON syntax: `python3 -c "import json; json.load(open('/home/aldo/.hermes/auth.json'))"`
2. Verify credentials are present: `grep access_token /home/aldo/.hermes/auth.json`
3. Test template rendering: `ansible-playbook --check --diff site.yml`
```
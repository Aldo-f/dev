# Security Reference: Ansible Vault Credential Patterns for Hermes

## Threat Model & Mitigations

| Threat | Mitigation | Implementation |
|--------|------------|----------------|
| Plaintext credentials in git | Ansible Vault encryption + .gitignore | `master.key` + vault file never committed |
| Vault password in CI logs | GitHub Secrets (masked) + `no_log: true` | `ANSIBLE_VAULT_MASTER_KEY` as secret |
| Credential drift between local & CI | Single source of truth in vault file | Base64 payload in `MASTER_CREDENTIALS_ENCRYPTED` |
| Missing/expired credentials at runtime | Nightly backup + validation step | Scheduled workflow + artifact retention |
| Accidental .env commit | `.gitignore` + code review enforcement | `vaults/master.key`, `.env*` ignored |
| Weak vault password | 32-char cryptographically random | `openssl rand -base64 32` |
| No audit trail | GitHub Actions logs + artifact storage | Workflow runs + downloadable JSON backups |

## Master Key Generation (One-time setup)

```bash
# 1. Generate cryptographically secure master password
openssl rand -base64 32 | tr -d '/+=' > dev/01-core-infra/vaults/master.key
chmod 600 dev/01-core-infra/vaults/master.key

# 2. Encrypt credential vault
ansible-vault encrypt dev/01-core-infra/vaults/hermes-credentials.yml \
  --vault-password-file dev/01-core-infra/vaults/master.key

# 3. Create GitHub Secrets
# ANSIBLE_VAULT_MASTER_KEY = cat dev/01-core-infra/vaults/master.key
# MASTER_CREDENTIALS_ENCRYPTED = cat dev/01-core-infra/vaults/hermes-credentials.yml | base64 -w 0
```

## Credential Structure (Jinja2 template variables)

```yaml
# vaults/hermes-credentials.yml (decrypted view)
hermes_credential_pool:
  openrouter:
    - id: "503f6e"
      access_token: "{{ vault_openrouter_503f6e }}"
      secret_fingerprint: "sha256:..."
  opencode-zen:
    - id: "52f84e"
      access_token: "{{ vault_opencode_zen_52f84e }}"
  # ... 18 provider types total
```

## Validation Commands

```bash
# Local validation
python3 -c "import json; d=json.load(open('~/.hermes/auth.json')); print(sum(len(v) for v in d['credential_pool'].values()))"

# CI validation (runs in workflow)
ansible-playbook --check --diff site.yml
```

## Emergency Recovery

If master key is lost:
1. Regenerate master key (openssl rand)
2. Re-encrypt credentials with new key
3. Update GitHub Secret `ANSIBLE_VAULT_MASTER_KEY`
4. Re-run workflow to re-deploy

If credential payload is corrupted:
1. Download latest artifact from GitHub Actions
2. Restore `hermes-credentials.yml` from backup JSON
3. Re-encrypt and push
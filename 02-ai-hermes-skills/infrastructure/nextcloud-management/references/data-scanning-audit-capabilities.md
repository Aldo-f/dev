# Nextcloud Data Scanning & Audit Capabilities

## Summary

**There is NO built-in automated scanner in Nextcloud that scans user file CONTENT for PII, sensitive data, or GDPR compliance patterns.** The available tools are:

| Tool/App | Purpose | Scans File Content? |
|----------|---------|---------------------|
| `admin_audit` (built-in, disabled by default) | Logs file access events, sharing actions, config changes, user admin actions | ❌ No - logs WHO did WHAT, not file contents |
| `occ files:scan` / `occ files:scan-app-data` | Indexes filesystem so files appear in UI | ❌ No - only updates database index |
| `files_antivirus` (built-in app) | Scans uploads for malware via ClamAV/ICAP | ❌ No - malware signatures only |
| `share_audit_dashboard` (3rd party app) | Visual audit of all shares, flags risky public links | ❌ No - share metadata only |
| Nextcloud Enterprise Compliance Kit | Data export/deletion requests, ToS tracking, admin manual | ❌ No - administrative workflows, not content scanning |

## What `admin_audit` Actually Does

When enabled (`occ app:enable admin_audit`), it logs to a separate audit.log (configurable via `occ config:app:set admin_audit logfile --value=/path/to/audit.log`):

- File access (read/download)
- File modifications (create/update/delete/move)
- Sharing events (create/accept/remove/modify shares)
- User management (create/delete/enable/disable/password reset)
- Group management
- Config changes
- Login/logout/failed login

**It does NOT**: Scan file contents for PII, credit cards, SSNs, health data, etc.

## Enterprise vs Community

Nextcloud **Enterprise** adds:
- Data Request app (users request export/deletion)
- Delete Account app
- Terms of Service enforcement
- Detailed admin manual (20+ pages)
- Direct support

But **no automated content scanner for PII/sensitive data** exists in either edition.

## External Solutions for PII/Sensitive Data Scanning

If you need to scan Nextcloud user data for PII/sensitive content, you must use external tools:

1. **PII Tools** (pii-tools.com) - Commercial, scans S3, local, databases, email
2. **Strac** - Cloud DLP, integrates with various stores
3. **Nightfall** - Commercial detection engine
4. **Open source**: Piiano Vault (storage for known-sensitive data), custom scripts with regex/ML models

## Typical Workflow for Compliance

1. Mount Nextcloud data directory externally (e.g., `/mnt/HDD1/nextcloud/data/`)
2. Run external scanner against the mounted filesystem
3. Generate reports for auditors
4. Use Nextcloud's Data Request/Delete Account apps for user-initiated actions
5. Use `admin_audit` logs for access tracking

## Verification Commands

```bash
# Enable audit logging
docker exec -u www-data nextcloud php occ app:enable admin_audit
docker exec -u www-data nextcloud php occ config:app:set admin_audit logfile --value=/var/log/nextcloud/audit.log

# Scan filesystem (indexing only)
docker exec -u www-data nextcloud php occ files:scan --all
docker exec -u www-data nextcloud php occ files:scan-app-data

# Check audit log
tail -f /var/log/nextcloud/audit.log
```
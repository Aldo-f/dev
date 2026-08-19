---
name: nextcloud-management
description: Manage, deploy, and troubleshoot Nextcloud instances.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Nextcloud, Docker, Infrastructure, Deployment, Troubleshooting, User Management]
    related_skills: [docker-volume-persistence]
---

# Nextcloud Management

## When to use
Use this skill for deploying, configuring, and troubleshooting Nextcloud instances, especially those running in Docker with external persistent volumes. This includes managing users, addressing permission issues, and resolving common deployment challenges.

## Key Learnings
- Deploying Nextcloud with Docker Compose involves specific configurations for persistent volumes and network setup.
- Persistent volume permissions are critical for Nextcloud data directories, often requiring specific `chown` commands after initial setup or recreation.
- Nextcloud user management can be complex when filesystem data already exists for a user not present in the database.
- When Nextcloud data appears "lost" after a container restart or HDD unmount, check for backup folders (e.g., `*_bak`) in the user's data directory before reinitializing - the data is often preserved and can be restored by moving contents from the backup to the live directory.
- **Password reset** (forgotten admin/user password): `docker exec -u www-data -e OC_PASS="$NEWPW" nextcloud php occ user:resetpassword --password-from-env <user>`. Always verify with a WebDAV PROPFIND: `curl -u "user:pass" -X PROPFIND -H "Depth: 1" http://host/remote.php/dav/files/<user>/` → HTTP 200. A 401 after reset usually means the earlier reset didn't survive a container restart (do-loop: reset password, curl, if 401 reset again).
- **Pi segfaults / "data lost" scare fix**: Apache/PHP worker segfaults (visible in `docker logs`) make the UI look empty/broken even though data is safe on disk. The persistent fix is (a) **pin the image to a stable tag** matching installed version (e.g. `nextcloud:34-apache` instead of `:latest`, so PHP minor bumps don't recur) and (b) **add Redis** for `memcache.distributed` + `memcache.locking` to offload the PHP workers (see reference). Restart the container to clear pending crash state.
- **Manifest-repos JSONC parsing fix**: When inline `//` comments appear in `templates/infra/repos.manifest.jsonc`, the Ansible `regex_replace('(?m)^\\\\s*//.*$\\\\n?', '')` only strips whole-line comments. To also strip trailing comments, use a pipeline: remove whole-line comments → protect `://` → strip `//...*` → restore `://` → `from_json`. This prevents the "Expecting property name enclosed in double quotes" error during `manifest-repos` role execution.
- **Media directory permissions for external downloads**: When external tools (e.g., Deezer downloader) write to Nextcloud's data directory, the target directory must exist and be writable by `www-data`. Create with `sudo mkdir -p /mnt/HDD1/nextcloud/data/aldo/files/media/music && sudo chown -R www-data:www-data /mnt/HDD1/nextcloud/data/aldo/files/media && sudo chmod -R 775 /mnt/HDD1/nextcloud/data/aldo/files/media`. Then trigger a scan: `docker exec -u www-data nextcloud php occ files:scan --path=aldo/files/media/music`.
- **Restore workflow when only a fresh/empty user home was created**: move `*_bak/files/*` into the live `files/` (same filesystem = instant, no 1.7TB copy), then re-scan with `occ files:scan --path=/<user>/files`. A full test via WebDAV/curl on the specific subfolder confirms what the web UI shows.

## References
- `references/redis-caching-and-tag-pinning.md` - Details Redis cache config and stable image tagging to avoid PHP segfaults.
- `references/automated-file-scan-cron.md` - Idempotent cron for `occ files:scan`.
- `references/hdd-mount-verification.md` - Details on verifying external HDD mounts with `nofail` in fstab.
- `references/instance-id-mismatch.md` - How to fix Nextcloud `instanceid` mismatch between `config.php` and `appdata_<instanceid>` directory.
- `references/nextcloud-host-header-fix.md` - Middleware to force Host header for Traefik proxy, fixing 502 errors.
- `references/user-recreation-issues.md` - Details a common problem with recreating Nextcloud users when their data directories already exist, and safe approaches to handle it.
- `references/deezer-nextcloud-integration.md` - Configuration for downloading Deezer playlists directly into Nextcloud data directory with proper permissions and scanning. **Includes case-sensitivity pitfall for Media/ vs media/ paths.**
- `references/data-scanning-audit-capabilities.md` - **No built-in PII/sensitive data content scanner exists.** Details what `admin_audit`, `files_antivirus`, `occ files:scan`, and Enterprise compliance features actually do vs. what they don't. Lists external tools for actual content scanning.

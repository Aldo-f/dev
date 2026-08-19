---
name: installer-robustness
category: devops
description: Robust installer patterns for piped curl deployments.
---

# Installer Robustness

**Trigger**: When deploying via `curl ... | bash` or similar piped installers that need to handle environment detection, git safety, and sudo appropriately. Also when managing storage devices including mounting, formatting, and persistent configurations.

**Key Patterns**:
- Detect execution context (piped vs direct) to resolve script directory.
- Hardcode installation path when necessary to avoid HOME variability.
- Validate execution as non-root user unless explicitly required.
- Use HTTPS for git operations in installers to avoid SSH key issues when run via sudo.
- **STORAGE MANAGEMENT**: When working with disks/partitions:
  - Use `lsblk -f` to inspect filesystem-aware device info
  - Identify persistent paths via `/dev/disk/by-id/*` symlinks (e.g., `/dev/disk/by-id/ata-WD_Elements_25A3_335A47503547595A-0:0`)
  - Create mount points with proper ownership: `sudo mkdir -p /mnt/<label>`
  - Mount filesystems with appropriate options: `sudo mount /dev/sdXN /mnt/<label>`
  - Verify with `mount | grep /mnt/<label>` and `df -h /mnt/<label>`
  - Configure persistent mounts via `/etc/fstab` with appropriate options
  - **DUCKDNS INTEGRATION**: When deploying container apps with DuckDNS domains:
    - Ensure traefik configuration includes both HTTP (80) and HTTPS (443) entrypoints
    - Add routing rules for DuckDNS domains with wildcard patterns where needed
    - Configure certificates via traefik's ACME resolver for automated SSL
    - Verify DNS propagation for domains like `cloud.aldof.duckdns.org`

**Docker Compose Deployment with External Networks**:
  - Ensure required Docker networks exist before deployment (e.g., `traefik_net`, `mongrelite_net`)
  - Use `docker compose up -d` with explicit paths when script is piped (not in interactive shell)
  - Use absolute paths for compose files when managing containers from scripts: `docker-compose -f /full/path/to/docker-compose.yml up -d`
  - When scripts are piped, `BASH_SOURCE` is undefined, so never rely on it for critical paths in install/deployment scripts
  - Use `_build_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)""` in piped contexts to get script directory

**Nextcloud-Specific Storage Pattern**: Store persistent user data on an external HDD mounted to `/mnt/HDD1/nextcloud/data`, with application files in a separate container-local volume. Create the directory structure: `06-apps-nextcloud/nextcloud/` for application code and `06-apps-nextcloud/db/` for databases. Set proper ownership for container access: `sudo chown -R 33:33 /mnt/HDD1/nextcloud/data`. Verify with `docker ps | grep nextcloud` and `docker exec nextcloud ls /var/www/html/data`.

**DUCKDNS ROUTING INTEGRATION**:
  - Add Nextcloud to traefik routing configuration:
```
nextcloud:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  service: nextcloud
  tls:
    certResolver: myresolver

nextcloud-http:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: nextcloud
```
  - Ensure HTTPS is enforced via redirect middleware
  - Add both nextcloud and nextcloud-http rules to maintain HTTP->HTTPS redirect chain
  - Test with `curl -I https://cloud.aldof.duckdns.org/` after DNS propagation

**Common Pitfalls in Storage + Docker Compose + DuckDNS**:
  - Mount option typos (`./nextcloud:/var/www/html` vs `./nextcloud:/var/www/html:rw`) can cause permission issues in containerized apps
  - Network connectivity failures: `ERROR: use of closed network connection` on docker networks indicates network configuration or firewall issues
  - Missing DuckDNS DNS propagation for new domain records
  - ACME certificate challenges failing due to DNS not pointing to the Pi's IP
  - For `docker compose` vs `docker-compose`: When scripts are piped, you can't rely on PATH resolution
  - Missing dependency verification: Always check for required packages before deployment (e.g., `docker`, `docker-compose`, system dependencies)
  - Container name conflicts when deploying multiple instances or after failed deployments
  - Mounting host directories without proper permissions causes `Permission denied` in containers
  - Network configuration issues: Ensure target networks exist before deploying services that depend on them

---
name: installer-robustness
category: devops
description: Robust installer patterns for piped curl deployments.
---

# Installer Robustness

**Trigger**: When deploying via `curl ... | bash` or similar piped installers that need to handle environment detection, git safety, and sudo appropriately. Also when managing storage devices including mounting, formatting, and persistent configurations.

**Key Patterns**:
- Detect execution context (piped vs direct) to resolve script directory.
- Hardcode installation path when necessary to avoid HOME variability.
- Validate execution as non-root user unless explicitly required.
- Use HTTPS for git operations in installers to avoid SSH key issues when run via sudo.
- **STORAGE MANAGEMENT**: When working with disks/partitions:
  - Use `lsblk -f` to inspect filesystem-aware device info
  - Identify persistent paths via `/dev/disk/by-id/*` symlinks (e.g., `/dev/disk/by-id/ata-WD_Elements_25A3_335A47503547595A-0:0`)
  - Create mount points with proper ownership: `sudo mkdir -p /mnt/<label>`
  - Mount filesystems with appropriate options: `sudo mount /dev/sdXN /mnt/<label>`
  - Verify with `mount | grep /mnt/<label>` and `df -h /mnt/<label>`
  - Configure persistent mounts via `/etc/fstab` with appropriate options
  - **DUCKDNS INTEGRATION**: When deploying container apps with DuckDNS domains:
    - Ensure traefik configuration includes both HTTP (80) and HTTPS (443) entrypoints
    - Add routing rules for DuckDNS domains with wildcard patterns where needed
    - Configure certificates via traefik's ACME resolver for automated SSL
    - Verify DNS propagation for domains like `cloud.aldof.duckdns.org`

**Docker Compose Deployment with External Networks**:
  - Ensure required Docker networks exist before deployment (e.g., `traefik_net`, `mongrelite_net`)
  - Use `docker compose up -d` with explicit paths when script is piped (not in interactive shell)
  - Use absolute paths for compose files when managing containers from scripts: `docker-compose -f /full/path/to/docker-compose.yml up -d`
  - When scripts are piped, `BASH_SOURCE` is undefined, so never rely on it for critical paths in install/deployment scripts
  - Use `_build_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)""` in piped contexts to get script directory

**Nextcloud-Specific Storage Pattern**: Store persistent user data on an external HDD mounted to `/mnt/HDD1/nextcloud/data`, with application files in a separate container-local volume. Create the directory structure: `06-apps-nextcloud/nextcloud/` for application code and `06-apps-nextcloud/db/` for databases. Set proper ownership for container access: `sudo chown -R 33:33 /mnt/HDD1/nextcloud/data`. Verify with `docker ps | grep nextcloud` and `docker exec nextcloud ls /var/www/html/data`.

**DUCKDNS ROUTING INTEGRATION**:
  - Add Nextcloud to traefik routing configuration:
```
nextcloud:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  service: nextcloud
  tls:
    certResolver: myresolver

nextcloud-http:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: nextcloud
```
  - Ensure HTTPS is enforced via redirect middleware
  - Add both nextcloud and nextcloud-http rules to maintain HTTP->HTTPS redirect chain
  - Test with `curl -I https://cloud.aldof.duckdns.org/` after DNS propagation

**Common Pitfalls in Storage + Docker Compose + DuckDNS**:
  - Mount option typos (`./nextcloud:/var/www/html` vs `./nextcloud:/var/www/html:rw`) can cause permission issues in containerized apps
  - Network connectivity failures: `ERROR: use of closed network connection` on docker networks indicates network configuration or firewall issues
  - Missing DuckDNS DNS propagation for new domain records
  - ACME certificate challenges failing due to DNS not pointing to the Pi's IP
  - For `docker compose` vs `docker-compose`: When scripts are piped, you can't rely on PATH resolution
  - Missing dependency verification: Always check for required packages before deployment (e.g., `docker`, `docker-compose`, system dependencies)
  - Container name conflicts when deploying multiple instances or after failed deployments
  - Mounting host directories without proper permissions causes `Permission denied` in containers
  - Network configuration issues: Ensure target networks exist before deploying services that depend on them

**Nextcloud-Specific Storage Pattern**:
  - Use dedicated directory structure: `06-apps-nextcloud/` for containerized apps
  - Separate application code from persistent user data
  - Mount persistent storage: `/mnt/HDD1/nextcloud/data:/var/www/html/data:rw`
  - Keep application files rebuild-friendly in container-local volumes
  - Create directory structure: `06-apps-nextcloud/nextcloud/` and `06-apps-nextcloud/db/`
  - Ensure proper ownership: `sudo chown -R 33:33 /mnt/HDD1/nextcloud/data` (www-data:www-data)
  - Verify with: `docker ps | grep nextcloud` and `docker exec nextcloud ls /var/www/html/data`

**Docker Compose Deployment with External Networks**:
  - Ensure required Docker networks exist before deployment (e.g., `traefik_net`, `mongrelite_net`)
  - Use `docker compose up -d` with explicit paths when script is piped (not in interactive shell)
  - Use absolute paths for compose files when managing containers from scripts: `docker-compose -f /full/path/to/docker-compose.yml up -d`
  - When scripts are piped, `BASH_SOURCE` is undefined, so never rely on it for critical paths in install/deployment scripts
  - Use `_build_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)""` in piped contexts to get script directory

**Common Pitfalls in Storage + Docker Compose**:
  - Mount option typos (`./nextcloud:/var/www/html` vs `./nextcloud:/var/www/html:rw`) can cause permission issues in containerized apps
  - Network connectivity failures: `ERROR: use of closed network connection` on docker networks indicates network configuration or firewall issues
  - For `docker compose` vs `docker-compose`: When scripts are piped, you can't rely on PATH resolution
  - Missing dependency verification: Always check for required packages before deployment (e.g., `docker`, `docker-compose`, system dependencies)
  - Container name conflicts when deploying multiple instances or after failed deployments
  - Mounting host directories without proper permissions causes `Permission denied` in containers
  - Network configuration issues: Ensure target networks exist before deploying services that depend on them

- For node dependencies, consider cleaning node_modules or using --ignore-scripts to avoid ENOENT errors.
- Ensure nodejs/npm are available via system packages when NVM environment may not be reliable.
- In automation (Ansible, scripts), ensure target directories are clean before cloning if a fresh state is required.
- Ensure required networks (e.g., Traefik) exist before deploying services.
- Install auxiliary tools (e.g., tree) via package manager for verification and debugging.
- In Ansible playbooks, check for existing node_modules before running npm ci to avoid unnecessary installs.
- When a repository contains only infrastructure files (no application source), copy template files rather than relying on the repo's content.
- **Never `git reset --hard` blindly in install.sh** — check `git merge-base --is-ancestor HEAD origin/main` first. If local has unpushed commits, warn and skip rather than destroying them.

**Git Reset Safeguard Pattern** (install.sh):
```bash
git fetch --depth=1 origin "$VERSION"
if git merge-base --is-ancestor HEAD "origin/$VERSION"; then
    git reset --hard "origin/$VERSION"
else
    echo "⚠ Local has unpushed commits — skipping git update."
fi
```

**UTILITY & DEBUGGING REFERENCE**:
- See `references/check-for-runnable-scripts.sh` for environment validation scripts
- See `references/npm-environments.md` for cross-environment npm patterns
- See `references/secure-curl-installation.md` for HTTPS-based install patterns
- See `references/docker-vs-compose-difference.md` for docker vs docker-compose deployment patterns
- See `references/launcher-fix.sh` for resolved loader issues

**ADDITIONAL BEST PRACTICES & WORKAROUND PATTERNS**:

**Cron Security & Best Practices**:
- Use absolute paths in cron to avoid $PATH dependencies
- Set up proper error handling and logging in cron scripts
- Implement version checking before script execution
- Use environment-specific config files for different deployment stages

**Piped Script Challenges & Solutions**:
- `BASH_SOURCE` is undefined when script is piped → always validate working directory
- Use `_build_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` to get script directory in piped contexts
- Never rely on `$HOME` in sudo contexts - explicitly define installation paths
- Use `sudo -E` to preserve environment variables needed for script execution
- Consider using `sudo --preserve-environment=PATH,HOME` for sudo scripts that need environment

**Advanced Storage Management**:
- For persistent storage across reboots, add entries to `/etc/fstab`
- Use UUIDs instead of device names for mount points: `/dev/disk/by-uuid/<UUID>`
- Configure static filesystem checks: `fsck -tfs ext4 /dev/sdXN`
- Create dedicated mount points with specific permissions: `mkdir -m 750 /mnt/storage`
- Use private TAs for secure storage management when possible

**DUCKDNS INTEGRATION BEST PRACTICES**:
- Always test DuckDNS updates manually before relying on them for critical services
- Use multiple DuckDNS domains for redundancy in production environments
- Set up monitoring for DNS propagation delays when using DuckDNS
- Configure backup DNS servers for critical services relying on DuckDNS

**Advanced Docker Compose Patterns**:
- Use environment-specific compose files (`docker-compose.dev.yml`, `docker-compose.prod.yml`)
- Validate network existence before service deployment:
```bash
if ! docker network ls | grep -q "<network-name>"; then
    docker network create <network-name> --driver bridge
fi
```
- Use absolute paths for compose files when running from scripts
- Implement compose file validation: `docker compose -f /path/to/compose.yml config`

**Environment-Specific Configuration Patterns**:
- Use `.env` files for local development
- Use environment variables for production configuration
- Implement configuration validation during startup
- Use secrets management for production environments

**Advanced Git Safety Patterns**:
- Use `git check-attr` to find files that need special handling
- Use `git filter-branch` for repository history cleaning (use with caution)
- Use `git rebase --abort` when aborting problematic rebases
- Store sensitive credentials in Git LFS for large files

**Performance Monitoring & Debugging**:
- Set up log rotation for long-running processes
- Use `strace` to debug system call issues in deployed applications
- Monitor resource usage: `top -p <pid>` or `htop`
- Implement health checks for critical services
- Use structured logging for better log analysis

**Special Tool Installation Patterns**:\n- For tools requiring specific installation methods (e.g., oh-my-openagent via bunx), use the exact command in automation with appropriate user context.\n  - Example: `bunx oh-my-openagent install --no-tui --claude no --openai no --gemini no --copilot no --platform opencode`\n  - This installs omo as a plugin for opencode with specific provider configurations\n  - Verification: `which omo` and `omo --help` should work\n  - Note that omo depends on opencode being installed first, so ensure opencode installation precedes omo installation\n  - In Ansible playbooks, use the `shell` module with `become_user` to run bunx as the target user\n  - Consider using the `creates` parameter to make the task idempotent (e.g., checks for a specific file that indicates successful installation)\n\n**Production Deployment Safety Patterns**:\n- Always test deployments in staging before production\n- Use feature flags for gradual rollouts\n- Implement blue-green deployments for zero-downtime updates\n- Use canary deployments for rolling out new features\n- Implement rollback mechanisms for failed deployments\n\n**Effective Solution Report Pattern for Init-Deep**:\n- Document the exact command that works: `omo /init-deep`\n- Document the required working directory: `/home/aldo/dev`\n- Document the expected output format for validation\n- Provide troubleshooting steps for common failures\n- Document the TDD approach for validation\n- Document the references to additional resources\n\n**Additional Utility Scripts**:\n\n**check-for-runnable-scripts.sh** - Environment validation before script execution\n**secure-curl-installation.md** - HTTPS-based install patterns\n**docker-vs-compose-difference.md** - Docker vs docker-compose deployment patterns\n**launcher-fix.sh** - Resolved loader issues\n
### JSON Extraction from Markdown and Resilient Parsing

When extracting JSON content that is embedded within a Markdown code block (e.g., from `web_extract` output or file reads), it's crucial to robustly parse the content. The `json` module can be strict, especially with large, potentially truncated inputs.

#### Workflow:

1.  **Read the full file**: If the output is truncated, always read the full content from the path provided (e.g., `/tmp/hermes-results/...` or `~/.hermes/cache/web/...`).
2.  **Extract the JSON string**: Use regular expressions to find the content between ````json` and ````.
    ```python
    import re
    # ... read content ...
    match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Fallback for cases where it might not be perfectly wrapped
        # or handle if the content itself is just raw JSON
        json_str = content.strip()
    ```
3.  **Use `json5` for robust parsing**: The standard `json` library can be strict. For more resilient parsing, especially when dealing with potentially malformed or truncated JSON from external sources, use `json5`.
    ```python
    import subprocess, sys
    # Ensure json5 is installed
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'json5', '-q'], stdout=subprocess.DEVNULL)
    import json5

    try:
        data = json5.loads(json_str)
        print('JSON parsed successfully with json5')
    except Exception as e:
        print(f'Failed to parse JSON with json5: {e}')
        # Add additional logging or error handling as needed
        raise
    ```

This approach makes JSON extraction and parsing more robust when dealing with varied and potentially problematic inputs from web scraping or API responses.

    certResolver: myresolver

nextcloud-http:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: nextcloud
```
  - Ensure HTTPS is enforced via redirect middleware
  - Add both nextcloud and nextcloud-http rules to maintain HTTP->HTTPS redirect chain
  - Test with `curl -I https://cloud.aldof.duckdns.org/` after DNS propagation

**Common Pitfalls in Storage + Docker Compose + DuckDNS**:
  - Mount option typos (`./nextcloud:/var/www/html` vs `./nextcloud:/var/www/html:rw`) can cause permission issues in containerized apps
  - Network connectivity failures: `ERROR: use of closed network connection` on docker networks indicates network configuration or firewall issues
  - Missing DuckDNS DNS propagation for new domain records
  - ACME certificate challenges failing due to DNS not pointing to the Pi's IP
  - For `docker compose` vs `docker-compose`: When scripts are piped, you can't rely on PATH resolution
  - Missing dependency verification: Always check for required packages before deployment (e.g., `docker`, `docker-compose`, system dependencies)
  - Container name conflicts when deploying multiple instances or after failed deployments
  - Mounting host directories without proper permissions causes `Permission denied` in containers
  - Network configuration issues: Ensure target networks exist before deploying services that depend on them

**Nextcloud-Specific Storage Pattern**:
  - Use dedicated directory structure: `06-apps-nextcloud/` for containerized apps
  - Separate application code from persistent user data
  - Mount persistent storage: `/mnt/HDD1/nextcloud/data:/var/www/html/data:rw`
  - Keep application files rebuild-friendly in container-local volumes
  - Create directory structure: `06-apps-nextcloud/nextcloud/` and `06-apps-nextcloud/db/`
  - Ensure proper ownership: `sudo chown -R 33:33 /mnt/HDD1/nextcloud/data` (www-data:www-data)
  - Verify with: `docker ps | grep nextcloud` and `docker exec nextcloud ls /var/www/html/data`

**Docker Compose Deployment with External Networks**:
  - Ensure required Docker networks exist before deployment (e.g., `traefik_net`, `mongrelite_net`)
  - Use `docker compose up -d` with explicit paths when script is piped (not in interactive shell)
  - Use absolute paths for compose files when managing containers from scripts: `docker-compose -f /full/path/to/docker-compose.yml up -d`
  - When scripts are piped, `BASH_SOURCE` is undefined, so never rely on it for critical paths in install/deployment scripts
  - Use `_build_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)""` in piped contexts to get script directory

**DUCKDNS ROUTING INTEGRATION**:
  - Add Nextcloud to traefik routing configuration:
```
nextcloud:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  service: nextcloud
  tls:
    certResolver: myresolver

nextcloud-http:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: nextcloud
```
  - Ensure HTTPS is enforced via redirect middleware
  - Add both nextcloud and nextcloud-http rules to maintain HTTP->HTTPS redirect chain
  - Test with `curl -I https://cloud.aldof.duckdns.org/` after DNS propagation

**Common Pitfalls in Storage + Docker Compose**:
  - Mount option typos (`./nextcloud:/var/www/html` vs `./nextcloud:/var/www/html:rw`) can cause permission issues in containerized apps
  - Network connectivity failures: `ERROR: use of closed network connection` on docker networks indicates network configuration or firewall issues
  - For `docker compose` vs `docker-compose`: When scripts are piped, you can't rely on PATH resolution
  - Missing dependency verification: Always check for required packages before deployment (e.g., `docker`, `docker-compose`, system dependencies)
  - Container name conflicts when deploying multiple instances or after failed deployments
  - Mounting host directories without proper permissions causes `Permission denied` in containers
  - Network configuration issues: Ensure target networks exist before deploying services that depend on them

- For node dependencies, consider cleaning node_modules or using --ignore-scripts to avoid ENOENT errors.
- Ensure nodejs/npm are available via system packages when NVM environment may not be reliable.
- In automation (Ansible, scripts), ensure target directories are clean before cloning if a fresh state is required.
- Ensure required networks (e.g., Traefik) exist before deploying services.
- Install auxiliary tools (e.g., tree) via package manager for verification and debugging.
- In Ansible playbooks, check for existing node_modules before running npm ci to avoid unnecessary installs.
- When a repository contains only infrastructure files (no application source), copy template files rather than relying on the repo's content.
- **Never `git reset --hard` blindly in install.sh** — check `git merge-base --is-ancestor HEAD origin/main` first. If local has unpushed commits, warn and skip rather than destroying them.

**Git Reset Safeguard Pattern** (install.sh):
```bash
git fetch --depth=1 origin "$VERSION"
if git merge-base --is-ancestor HEAD "origin/$VERSION"; then
    git reset --hard "origin/$VERSION"
else
    echo "⚠ Local has unpushed commits — skipping git update."
fi
```

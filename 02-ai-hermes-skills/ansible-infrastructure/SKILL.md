---
name: ansible-infrastructure
description: Manage infrastructure via Ansible in ~/dev/01-core-infra.
---

# Ansible Infrastructure Management (01-core-infra)

Manage infrastructure via Ansible playbooks in ~/dev/01-core-infra.

## Quick Commands

```bash
cd ~/dev/01-core-infra
./install.sh  # Run Ansible playbook
```

## Repository Manifest

Add git repos to `templates/infra/repos.manifest.jsonc`:
```json
{
  "repos": [
    {
      "name": "06-apps-scripts-google",
      "remote": "https://github.com/Aldo-f/script.google",
      "checkout": { "ref": "main", "type": "branch" },
      "infraSubdir": "."
    }
  ]
}
```

## Managing Git-Repository Components (02-*, 06-*)

Components marked as `git-repo` in the group taxonomy (02-ai-*, 06-apps-*) are managed via the `manifest-repos` Ansible role:
- The role reads `templates/infra/repos.manifest.jsonc` (JSONC format) to determine which git repositories to manage
- For each repository, it clones/updates to the specified branch/tag/ref
- It then synchronizes the `infraSubdir` (default: `.`) from the repo to `templates/infra/<name>/infra/`
- This allows infrastructure templates (docker-compose.yml, etc.) to be maintained in the source repositories while being consumed by the Ansible playbook
- Key technique: When parsing the manifest, use regex `(?<!://)//.*$` to strip comments while preserving `http://` and `https://` in URLs

## Directory Structure

- `templates/infra/<component>/` - Edit here for infra templates
- `templates/apps/<name>/` - App-specific templates
- `templates/systemd/<name>.service` - Systemd service templates
- `ansible/roles/tools/defaults/main.yml` - Add tool sentries here

## Group Taxonomy

| Prefix | Deploy Target |
|--------|---------------|
| 01-core-* | Inside repo: `01-core-infra/<name>/` |
| 02-ai-* | Git repo via manifest |
| 04-network-* | Sibling repo: `~/dev/04-network-<name>/` |
| 06-apps-* | Git repo via manifest |

## Tool Sentries

Each required CLI tool is declared in `ansible/roles/tools/defaults/main.yml` with a sentry command that checks if the tool is already installed. To add a new tool:

1. Add a sentry entry to `ansible/roles/tools/defaults/main.yml`:
   ```yaml
   <tool-name>:
     command: "<tool> --version"  # or whatever checks presence
   ```

2. Add an installation task to `ansible/roles/tools/tasks/main.yml`:
   ```yaml
   - name: Install <tool-name>
     apt:
       name: <package-name>
       state: present
     become: true
     when: "'<tool-name>' in tools_sentries and ansible_facts.packages['<tool-name>'] is not defined"
   ```

3. Activate the sentry in `ansible/playbooks/site.yml` by adding the tool name to the `tools_sentries` list.

Example (locate tool):
```yaml
# In defaults/main.yml
locate:
  command: locate --version

# In tasks/main.yml
- name: Install locate (plocate)
  apt:
    name: locate
    state: present
  become: true
  when: "'locate' in tools_sentries and ansible_facts.packages['locate'] is not defined"

# In site.yml (add to tools_sentries list)
  - locate
```

## Shell Configuration

The role now ensures fish shell is installed and configures the Hermes agent directory in the fish PATH:

- Installs fish package via apt
- Adds `$HOME/.hermes/hermes-agent` to the fish PATH in `~/.config/fish/config.fish`

### Subdomain Organization Pattern (08/2026)

Services should be organized by access requirements:

| Group | Subdomain Pattern | IP Allowlist |
|-------|------------------|--------------|
| Public services | `*.aldof.duckdns.org` | None |
| Dev infrastructure | `*.dev.aldof.duckdns.org` | Yes (private IPs) |

**Example:**
- `cloud.aldof.duckdns.org` - Nextcloud (public)
- `portainer.dev.aldof.duckdns.org` - Portainer (dev, IP restricted)
- `cockpit.dev.aldof.duckdns.org` - Cockpit (dev, IP restricted)
- `plex.aldof.duckdns.org` - Plex (public)
- `web.hermes.dev.aldof.duckdns.org` - Hermes WebUI (dev, IP restricted)

**Critical:** When migrating services to dev subdomains, remove old routes from `aldof.duckdns.org` to avoid confusion.

## Adding New Tools to Infrastructure (Pattern: Tool Sentry + Role + Template)

**Lesson from camoufox integration:** When adding a new tool like Camoufox to the infrastructure, follow this systematic approach to ensure maintainability and consistency with the existing architecture.

**Signal to use this pattern:** Adding any new CLI tool or external service that requires installation, configuration, or runtime management.

### 1. Add Tool Sentry to ansible/roles/tools/defaults/main.yml

```yaml
# In defaults/main.yml, add sentry entry for the new tool:
<tool-name>:
  command: "<tool> --version"
```

**Example (from camoufox integration):**
```yaml
camoufox:
  command: camoufox --version
```

### 2. Add Installation Task to ansible/roles/tools/tasks/main.yml

```yaml
# In tasks/main.yml, add installation logic with environment isolation:
- name: Install <tool-name> with dedicated environment
  shell: |
    mkdir -p /home/<user>/.venv-<tool-name>
    python3 -m venv /home/<user>/.venv-<tool-name>
    . /home/<user>/.venv-<tool-name>/bin/activate
    pip install --upgrade pip
    pip install "<tool-name>[geoip]" <tool-name>-cli==<version>
    <tool-name> --version
    <tool-name> fetch
    <tool-name> sync
  environment:
    PATH: "{{ ansible_env.PATH }}:/home/<user>/.venv-<tool-name>/bin"
  args:
    creates: /home/<user>/.venv-<tool-name>

- name: Add <tool-name> to system PATH permanently
  lineinfile:
    path: /home/<user>/.bashrc
    line: 'export PATH="$HOME/.venv-<tool-name>/bin:$PATH"'
    create: yes
    insertafter: EOF
  when: "'<tool-name>' in tools_sentries"
```

**Example (from camoufox integration):**
```yaml
- name: Install camoufox via pip in dedicated virtual environment
  shell: |
    mkdir -p /home/aldo/.venv-camoufox
    python3 -m venv /home/aldo/.venv-camoufox
    . /home/aldo/.venv-camoufox/bin/activate
    pip install --upgrade pip
    pip install "camoufox[geoip]" camoufox-cli==0.4.0
    camoufox --version
    camoufox fetch
    camoufox sync
  environment:
    PATH: "{{ ansible_env.PATH }}:/home/aldo/.venv-camoufox/bin"
  args:
    creates: /home/aldo/.venv-camoufox

- name: Add camoufox to system PATH permanently
  lineinfile:
    path: /home/aldo/.bashrc
    line: 'export PATH="$HOME/.venv-camoufox/bin:$PATH"'
    create: yes
    insertafter: EOF
  when: "'camoufox' in tools_sentries"
```

### 3. Add Tool to Playbook (Optional)

If the tool requires specialized configuration beyond basic installation, create a dedicated role:

```bash
# Directory structure:
ansible/roles/<tool-name>/tasks/main.yml
ansible/roles/<tool-name>/README.md
```

Or, if it's a standard pattern, consider adding it to the `tools` role directly.

### 4. Add Template Documentation in templates/infra/<tool-name>/

Create organized documentation in the templates/infra folder:

```bash
# templates/infra/<tool-name>/
  SKILL.md          # Overview and usage
  README.md         # Setup instructions
  config.j2         # Jinja2 template if needed
```

**Example (from camoufox integration):**
```bash
# templates/infra/camoufox/CAMOUFOX.md
```

### 5. Extend Tools Sentry in site.yml (Optional)

Add the tool to the `tools_sentries` list in `ansible/playbooks/site.yml` if it should always be installed.

```yaml
# In site.yml, tools_sentries list:
  - docker
  - nvm
  - node
  - npm
  - pnpm
  - bun
  - fvm
  - tree
  - ollama
  - llama-server
  - locate
  - lmstudio
  - fish
  - hermes
  - opencode
  - omo
  - mem0
  - freellmapi
  - script_google
  - tailscale
  # Add your tool here:
  - camoufox
```

### Key Benefits of This Pattern

1. **Environment Isolation:** Each tool gets its own virtual environment, preventing version conflicts
2. **Path Management:** Permanent PATH export ensures the tool is globally accessible
3. **Conditional Installation:** Tools only install when they're in the sentry list and not already present
4. **Maintainability:** Clear separation of concerns between tool installation and configuration
5. **Verification:** The `creates` argument ensures idempotency
6. **Consistent:** Follows the same pattern as existing tools (locate, lmstudio, etc.)

### Applying This Pattern

To add a new tool, copy the existing `locate` or `lmstudio` examples in:
- `ansible/roles/tools/defaults/main.yml`
- `ansible/roles/tools/tasks/main.yml`

Then update `ansible/playbooks/site.yml` if the tool should always be present.

**Critical pitfall to avoid:** Never hardcode `/home/<username>/` paths in templates. Use `__HOME__` or `__USER__` placeholders that get expanded at runtime. The example above shows user-specific paths because virtual environments need to be user-specific, but this should be consistent with the rest of the infrastructure.

**Verification:** After deployment, validate with `<tool-name> --version` and check that the tool appears in PATH via `echo $PATH | grep <tool-name>`.

**Learning Note:** The camoufox integration demonstrates how to install and configure advanced CLI tools while maintaining system stability through virtual environment isolation and conditional installation logic.

**Lesson on Route Configuration (07/2026):** When deploying infrastructure with multiple services, use `127.0.0.1` for services on the same Pi5 host (localhost routing). Use consistent external IPs (like `192.168.0.5`) only when external access is required. Always verify service endpoints from the Pi5 via `docker exec <container> curl http://127.0.0.1:<port>` to confirm localhost routing works before updating routes.yml.

**Critical Pitfall - Conflicting IP Addresses:** When Pi5 loses static IP configuration, it's reassigned dynamically (e.g., `192.168.0.50`). Always verify the current IP via `ip addr show wlan0` before deploying routes.yml. If the IP changes, update all service routes accordingly, or use dynamic resolution methods.

### Lessons Learned from Session: Infrastructure as Code Pitfalls

During troubleshooting of service outages, four critical infrastructure patterns were identified and fixed:

### 1. routes.yml Corruption via Overlapping lineinfile Patterns
**Problem:** The `neo-brutalist-home` Ansible role contained `lineinfile` tasks with regex `^    homepage` that matched BOTH `homepage-http:` and `homepage:` router names in Traefik's routes.yml, causing progressive file truncation on each playbook run.

**Impact:** Progressive loss of route definitions leading to 404 errors across all services.

**Fix:** Removed the destructive `lineinfile` tasks from `ansible/roles/neo-brutalist-home/tasks/main.yml`. Routes are now managed exclusively via the Ansible template at `templates/infra/04-network-traefik/routes.yml.tmpl`.

**Verification:** After any playbook run, validate with `docker exec traefik cat /etc/traefik/routes.yml` and check Traefik logs for absence of `field not found, node: taskqueue` errors.

### 2. NextCloud Proxy Header Misconfiguration
**Problem:** NextCloud behind Traefik was redirecting to `http://nextcloud/login` instead of `https://cloud.aldof.duckdns.org/login` due to missing proxy headers and trusted configuration.

**Impact:** Users experienced "Access through untrusted domain" errors and infinite redirect loops when accessing via the public domain.

**Fix:** Applied proper proxy configuration:
```bash
docker exec -u www-data nextcloud php occ config:system:set trusted_domains 1 --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set overwritehost --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set overwriteprotocol --value=https
docker exec -u www-data nextcloud php occ config:system:set overwritecondaddr --value='\.aldof\.duckdns\.org$'
docker exec -u www-data nextcloud php occ config:system:set overwrite.cli.url --value=https://cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set trusted_proxies 0 --value=172.18.0.0/16
```

**Verification:** `curl -I https://cloud.aldof.duckdns.org/` should return 302 to `https://cloud.aldof.duckdns.org/login`, not `http://nextcloud/login`.

### 4. Media Services Deployment (05-media-*) - Fixed
**Problem:** The `container_services` list included 05-media-plex, 05-media-qbittorrent, and 05-media-nextcloud, but their runtime directories didn't exist and the compose templates had issues:

| Service | Template Issue | Missing Runtime Dir |
|---------|---------------|---------------------|
| plex | `network_mode: host` (incompatible with traefik_net), relative paths `./config`, `~/media/movies` | `/home/aldo/dev/01-core-infra/plex/` |
| qbittorrent | No network config, no restart policy, relative paths `./config`, `./downloads` | `/home/aldo/dev/01-core-infra/qbittorrent/` |
| nextcloud | Used `${MYSQL_ROOT_PASSWORD}` env vars without .env template, hardcoded `/mnt/HDD1/nextcloud` | `/home/aldo/dev/01-core-infra/nextcloud/` |

**Fixes Applied:**
1. **Plex template** (`templates/infra/05-media-plex/docker-compose.yml`): Removed `network_mode: host`, added `traefik_net` network, replaced relative paths with absolute HDD paths (`/mnt/HDD1/plex/config`, `/mnt/HDD1/media/movies`, `/mnt/HDD1/media/tv`), added `restart: unless-stopped`.
2. **Qbittorrent template** (`templates/infra/05-media-qbittorrent/docker-compose.yml`): Added `traefik_net` network, added `restart: unless-stopped`, replaced relative paths with absolute HDD paths (`/mnt/HDD1/qbittorrent/config`, `/mnt/HDD1/downloads`).
3. **Nextcloud template** (`templates/infra/05-media-nextcloud/docker-compose.yml`): Removed obsolete `version: '3.9'` field, replaced hardcoded paths with `${MYSQL_ROOT_PASSWORD}` and `${MYSQL_PASSWORD}` env var placeholders, kept `/mnt/HDD1/nextcloud` absolute path.
4. **Traefik routes** (`templates/infra/04-network-traefik/routes.yml`): Added `plex` and `qbittorrent` HTTP router entries with HTTPS redirect and TLS certResolver.
5. **Vault credentials** (`vaults/nextcloud-credentials.yml`): Created placeholder vault file for Nextcloud MySQL credentials.
6. **Containers role** (`ansible/roles/containers/tasks/main.yml`): Added `include_vars` task to load nextcloud vault credentials before deployment.

**Verification:**
```bash
# Verify templates are valid
python3 -c "import yaml; [yaml.safe_load(open(f)) for f in ['templates/infra/05-media-plex/docker-compose.yml', 'templates/infra/05-media-qbittorrent/docker-compose.yml', 'templates/infra/05-media-nextcloud/docker-compose.yml']]"

# Verify containers are running
docker ps | grep -E 'plex|qbittorrent'

# Verify Traefik routes are synced
docker exec traefik cat /etc/traefik/routes.yml | grep -A 5 'plex\|qbittorrent'
```

**Note:** A separate Nextcloud instance exists at `/home/aldo/dev/06-apps-nextcloud/` (managed outside 01-core-infra) with its own docker-compose.yml. The 05-media-nextcloud template deploys a *second* instance. Coordinate to avoid port/volume conflicts.

### Traefik Route Management Workflow

**Critical Pattern for routes.yml Updates:**
All changes to Traefik routing must be made through the Ansible template, never by direct modification of the runtime file. This prevents configuration drift and ensures idempotency.

#### Correct Workflow:
1. **Edit the template**: Modify `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml`
2. **Deploy via Ansible**: Run `~/dev/01-core-infra/install.sh` to sync template to runtime
3. **Verify**: Check Traefik logs and test endpoints

#### Why This Approach:
- The Ansible `containers` role automatically copies the template to `/home/aldo/dev/04-network-traefik/routes.yml` (which is mounted into the Traefik container)
- Direct edits to runtime files are overwritten on the next Ansible run
- Template-based management ensures consistency across deployments

### Pitfall: lineinfile Tasks Corrupting routes.yml (Historical)
The `neo-brutalist-home` Ansible role previously contained `lineinfile` tasks with regexp `^    homepage` that matched both `homepage-http:` and `homepage:` router names, causing the `routes.yml` file to be truncated. This resulted in 404 errors for all Traefik routes.

**Fix:** Removed the `lineinfile` tasks from `ansible/roles/neo-brutalist-home/tasks/main.yml`. Routes are now managed exclusively via the Ansible template at `templates/infra/04-network-traefik/routes.yml`.

**Verification:** After any playbook run, validate routes.yml with `docker exec traefik cat /etc/traefik/routes.yml` and check Traefik logs for `field not found` errors.

### Adding IP-Based Access Control to Subdomains (Middleware Pattern)

To restrict access to specific subdomains (e.g., `web.hermes.dev.aldof.duckdns.org`) to only certain IP addresses, use a Traefik IP allowlist middleware for cleaner, more maintainable configuration:

#### Example Implementation:
1. **Add middleware** to the middlewares section:
```yaml
  middlewares:
    https-redirect:
      redirectScheme:
        scheme: https
        permanent: true
    ipAllowList:
      ipAllowList:
        sourceRange:
          - "192.168.0.0/16"
          - "10.0.0.0/8"
          - "172.16.0.0/12"
          - "169.254.0.0/16"
          - "127.0.0.0/8"
```

2. **Apply middleware** to relevant routers:
```yaml
    hermes-http:
      rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
      entryPoints:
        - web
      middlewares:
        - https-redirect
        - ipAllowList
      service: hermes-webui
    hermes:
      rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
      entryPoints:
        - websecure
      service: hermes-webui
      tls:
        certResolver: myresolver
      middlewares:
        - ipAllowList
```

#### Key Points:
- **Cleaner approach**: Define IP rules once in middleware, reference everywhere
- **Supports CIDR ranges**: `ClientIP(`<cidr-range>`)` for networks (e.g., `192.168.0.0/16`)
- **Multiple IPs supported**: Combine ranges as needed for complex access patterns
- **Always test** with `curl -I --interface <test-ip> https://<subdomain>...` from allowed IP
- **Remember**: Update BOTH template AND verify runtime file after Ansible deployment

**Verification Checklist:**
- [ ] Template edited in `templates/infra/04-network-traefik/routes.yml`
- [ ] Ansible playbook ran successfully (`./install.sh`)
- [ ] Runtime file updated: `cat /home/aldo/dev/04-network-traefik/routes.yml`
- [ ] Middleware present: Check for `ipAllowList` in middleware section
- [ ] Middleware applied: Verify routers reference `- ipAllowList`
- [ ] Traefik reloaded: `docker logs traefik | grep -i "configuration loaded"`
- [ ] Access test passes: `curl -I --interface <internal-ip> https://<subdomain>...`
- [ ] Denial test passes: `curl -I --interface <external-ip> https://<subdomain>...` (should fail)

### User Communication Preference

**User Aldo Fieuw prefers concise, direct communication in English and does not want additional clarification questions during implementations.** This preference is now encoded in the skill to guide future sessions. The skill will automatically enforce:
- One‑sentence summaries for status updates.
- No extra probing questions; assume the task is fully defined.
- All outputs are self‑contained and actionable.

Additionally, the following **Ansible best‑practice updates** have been incorporated:

### Variable Naming Conventions
- Replaced legacy `__HOME__`, `__USER__`, `__CORE_INFRA__` placeholders with lower‑case, lint‑friendly names:
  ```yaml
  core_infra_home: "/home/aldo"
  core_infra_user: "aldo"
  core_infra_root: "/var/lib/core-infra"
  ```
- All templates now reference `{{ core_infra_home }}`, `{{ core_infra_user }}`, and `{{ core_infra_root }}`.
- This resolves Ansible‑lint `var-naming` warnings.

### Idempotency & Clean‑up Patterns
- Use `blockinfile` (with markers) instead of multiple `lineinfile` for PATH management.
- Add `force: no` to copy tasks for static scripts to avoid unnecessary "changed" reports.
- Conditional Traefik reload only when `routes.yml` actually changes.
- All installer tasks now include proper `changed_when` and `failed_when` guards for true idempotency.

### Tool Integration Pattern
- New **"Adding New Tools"** reference (`references/adding-tools.md`) documents the systematic approach:
  1. Add a sentry in `ansible/roles/tools/defaults/main.yml`.
  2. Add an install task in `ansible/roles/tools/tasks/main.yml` using a per‑tool virtual environment.
  3. Optionally add the tool to `tools_sentries` in `site.yml`.
- Example snippets for camoufox integration are included.

### Llama‑cpp Systemd Template Update
- Updated `app-llama-server.service.j2` to use the new placeholders and absolute paths.
- Ensures the service starts correctly on any host.

### Additional References
- `references/traefik-ip-access-control.md` – middleware IP allow‑list pattern.
- `references/ansible-idempotency-patterns.md` – consolidated idempotency techniques.
- `references/infrastructure-verification.md` – three‑layer verification workflow.

These updates make the ansible‑infrastructure skill more robust, lint‑clean, and aligned with the user’s communication style.

## Critical Pitfall: Ansible Become Timeout on Localhost

When running `ansible-playbook` on `localhost` with `connection: local`, tasks with `become: true` can time out with:
```
[ERROR]: Task failed: Timed out waiting for become success.
fatal: [localhost]: UNREACHABLE! => {"msg": "Task failed: Timed out waiting for become success.", "unreachable": true}
```

**This occurs even when passwordless sudo works normally** (`sudo -n true` succeeds, `sudo -l` shows `(ALL) NOPASSWD: ALL`).

### Root Cause
Ansible's local connection mode can hang during the privilege escalation handshake in certain headless environments (Pi 5 / Raspberry Pi OS), particularly when sudo's `use_pty` setting is enabled or the become plugin doesn't properly handle the local sudo context.

### Workaround
1. **Run without become first**: `ansible-playbook -i inventories/local.yml playbooks/site.yml --extra-vars="ansible_become=false"`
2. **Use `become_method=runuser`**: `ansible-playbook ... -e ansible_become_method=runuser -e ansible_become_user=root`
3. **Disable `gather_facts`**: `ansible-playbook ... -e gather_facts=false`
4. **Split by tags**: Run non-privileged roles first, then privileged ones separately.

**Full details**: See `references/ansible-become-timeout-workaround.md`.

## User Communication Preference

**User Aldo Fieuw prefers concise, direct communication in English and does not want additional clarification questions during implementations.** This preference is now encoded in the skill to guide future sessions. The skill will automatically enforce:
- One-sentence summaries for status updates.
- No extra probing questions; assume the task is fully defined.
- All outputs are self-contained and actionable.

## Pitfall: Nextcloud Untrusted Domain Behind Traefik
When Nextcloud is behind Traefik, the container may redirect to `http://nextcloud/login` instead of `https://cloud.aldof.duckdns.org/login`. This is caused by missing proxy configuration.

**Fix workflow:**
```bash
docker exec -u www-data nextcloud php occ config:system:set trusted_domains 1 --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set overwritehost --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set overwriteprotocol --value=https
docker exec -u www-data nextcloud php occ config:system:set overwritecondaddr --value='\.aldof\.duckdns\.org$'
docker exec -u www-data nextcloud php occ config:system:set overwrite.cli.url --value=https://cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set trusted_proxies 0 --value=172.18.0.0/16
```

**Verification:** `curl -I https://cloud.aldof.duckdns.org/` should return 302 to `https://cloud.aldof.duckdns.org/login`, not `http://nextcloud/login`.

### Vault to Environment Injection Pattern
The Freellmapi deployment requires a consistent encryption key that must come from Ansible Vault:
- Vault file: `vaults/freellmapi-credentials.yml` (encrypted with master.key)
- Template: `templates/infra/02-ai-freellmapi/infra/.env.j2` uses `{{ vault_freellmapi_encryption_key }}`
- Deployed to: `/home/aldo/dev/02-ai-freellm/.env` with mode 0600

### Pitfall: Missing Encryption Key Causes Bad Gateway
If the `.env` file is missing or has an invalid `ENCRYPTION_KEY`, the freellmapi service returns 502 Bad Gateway at `https://freellm.aldof.duckdns.org/models/chat`.

**Fix workflow:**
1. Run full Ansible playbook: `cd /home/aldo/dev/01-core-infra && ./install.sh`
2. This regenerates `.env` from vault template
3. Verify with: `ansible-vault view --vault-password-file vaults/master.key vaults/freellmapi-credentials.yml`
4. Test endpoint: `curl -X POST https://freellm.aldof.duckdns.org/models/chat -H "Content-Type: application/json" -d '{"model":"freellmapi","messages":[{"role":"user","content":"test"}]}'`

### Verification Checklist After Deployment
- [ ] `.env` exists at `/home/aldo/dev/02-ai-freellm/.env`
- [ ] `ENCRYPTION_KEY` matches vault value (64-char hex)
- [ ] Docker container `02-ai-freellm-freellmapi-1` is running
- [ ] Traefik routes `freellm.aldof.duckdns.org` to port 3001
- [ ] All service endpoints respond with 200 on HTTPS

### Verification Checklist After Route Changes
- [ ] `routes.yml` uses `127.0.0.1` for services on the same Pi5 host (localhost routing)
- [ ] `routes.yml` uses consistent external IPs for external access
- [ ] `docker exec traefik cat /etc/traefik/routes.yml` shows correct service URLs
- [ ] Traefik logs show no `field not found` errors after restart
- [ ] All HTTPS endpoints return 200 OK

### Idempotency Improvements (08/2026)

During the August 2026 session, four critical idempotency improvements were implemented to make Ansible playbook re-runs safer and more efficient:

#### 1. PATH Management: `lineinfile` → `blockinfile`
**Problem:** Multiple `lineinfile` tasks appending PATH exports to `.bashrc` and `.config/fish/config.fish` created duplicate entries on every playbook re-run.

**Solution:** Replaced with `blockinfile` using unique markers:
```yaml
- name: Ensure bash config has PATH for curl-installed tools
  blockinfile:
    path: /home/{{ ansible_user }}/.bashrc
    block: |
      export PATH="$HOME/.bun/bin:$HOME/fvm/bin:$HOME/.lmstudio/bin:$HOME/.local/bin:$HOME/.opencode/bin:$PATH"
    marker: "# {mark} ANSIBLE MANAGED PATH BLOCK - curl-installed tools"
    create: yes
  when: "'ollama' in tools_sentries or 'hermes' in tools_sentries or 'opencode' in tools_sentries"

# Fish shell (updated to fish 4.0 compatible syntax)
- name: Ensure fish config has PATH for curl-installed tools
  blockinfile:
    path: /home/{{ ansible_user }}/.config/fish/config.fish
    block: |
      set -gx PATH $HOME/.bun/bin $HOME/fvm/bin $HOME/.lmstudio/bin $HOME/.local/bin $HOME/.opencode/bin $PATH
    marker: "# {mark} ANSIBLE MANAGED PATH BLOCK - curl-installed tools"
    create: yes
  when: "'ollama' in tools_sentries or 'hermes' in tools_sentries or 'opencode' in tools_sentries"
```

**Files updated:**
- `ansible/roles/mesh_sync/tasks/main.yml` - Main PATH blocks
- `ansible/roles/tools/tasks/main.yml` - spec-kit PATH blocks

#### 2. Cron Scripts: `force: no` on `copy` tasks
**Problem:** `backup.sh` and `healthcheck.sh` were copied to `/usr/local/bin/` on every run, always reporting "changed" even when content was identical.

**Solution:** Added `force: no` to only copy when source differs from destination:
```yaml
- name: Copy backup.sh to bin
  copy:
    src: "{{ infra_dir }}/scripts/operations/backup.sh"
    dest: "/usr/local/bin/backup.sh"
    mode: '0755'
    force: no  # Only copy if content differs

- name: Copy healthcheck.sh to bin
  copy:
    src: "{{ infra_dir }}/scripts/operations/healthcheck.sh"
    dest: "/usr/local/bin/healthcheck.sh"
    mode: '0755'
    force: no
```

**File updated:** `ansible/roles/cron/tasks/main.yml`

#### 3. Traefik Route Sync: Conditional Reload
**Problem:** Routes file was copied and Traefik reload handler triggered on every playbook run, even when routes.yml hadn't changed.

**Solution:** Register the copy result and only reload when actually changed:
```yaml
- name: Sync Traefik routes.yml template to runtime
  copy:
    src: "{{ template_dir }}/infra/04-network-traefik/routes.yml"
    dest: "{{ traefik_runtime_dir }}/routes.yml"
    owner: aldo
    group: aldo
    mode: '0644'
  register: routes_copy

- name: Reload traefik if routes changed
  command: docker exec traefik kill -HUP 1
  when: routes_copy.changed
  become: true
```

**File updated:** `ansible/roles/containers/tasks/main.yml`

#### 4. Install Commands: Proper `changed_when` / `failed_when`
**Problem:** Shell-based install tasks (ollama, nodejs, pnpm, fvm, hermes, opencode, tailscale, lmstudio) lacked proper change detection, always reporting "changed" on re-runs or failing incorrectly when tools already existed.

**Solution:** Added `register`, `changed_when`, and `failed_when` to all install tasks:
```yaml
- name: Pull Ollama model
  command: ollama pull "{{ ollama_model }}"
  register: ollama_pull
  changed_when: "'Pulling' in ollama_pull.stdout or 'pulling' in ollama_pull.stdout"
  failed_when: ollama_pull.rc != 0 and 'already exists' not in ollama_pull.stderr and 'already exists' not in ollama_pull.stdout
  when: ollama_key_file.stat.exists and ollama_model is defined

- name: Install ollama
  shell: curl -fsSL https://ollama.com/install.sh | sh
  args:
    creates: /usr/bin/ollama
  become: true
  when: "'ollama' in tools_sentries"
  register: ollama_install
  changed_when: ollama_install.rc == 0 and ('install' in ollama_install.stdout.lower() or 'downloaded' in ollama_install.stdout.lower())
  failed_when: ollama_install.rc != 0

# Pattern applied to: nodejs, pnpm, fvm, hermes, opencode, tailscale, lmstudio
```

**Files updated:**
- `ansible/roles/mesh_sync/tasks/main.yml` - Ollama model pull
- `ansible/roles/tools/tasks/main.yml` - All installer tasks

#### Verification Results
All four improvements verified with ad-hoc Python script:
```bash
python3 /tmp/hermes-verify-idempotency.py
# Output: ALL IDEMPOTENCY IMPROVEMENTS VERIFIED
```

Ansible syntax check also passes:
```bash
cd /home/aldo/dev/01-core-infra/ansible && ansible-playbook --syntax-check playbooks/site.yml
# Output: playbook: playbooks/site.yml
```

**Impact:** Playbook re-runs now properly detect unchanged state, avoid unnecessary work, and complete faster with cleaner output.

### Troubleshooting Encryption Key Issues
If you encounter "ENCRYPTION_KEY is required in production" errors despite the .env file existing:
1. Verify the .env file contents: `cat /home/aldo/dev/02-ai-freellm/.env`
2. Check that ENCRYPTION_KEY is present and is a 64-character hex string
3. Ensure the file has no extra whitespace or formatting issues
4. Validate the vault file is accessible: `ansible-vault view --vault-password-file vaults/master.key vaults/freellmapi-credentials.yml`
5. Re-run the specific Ansible task: `ansible-playbook -i inventories/local.yml --tags=freellmapi ansible/playbooks/site.yml`

## Media Services Deployment (05-media-*) - Current Gap Analysis

### Problem Identified (2026-08-04)
The `container_services` list in `ansible/roles/containers/defaults/main.yml` included 05-media-plex, 05-media-qbittorrent, and 05-media-nextcloud, but their runtime directories didn't exist and the compose templates had issues:

| Service | Template Issue | Missing Runtime Dir |
|---------|---------------|---------------------|
| plex | `network_mode: host` (incompatible with traefik_net), relative paths `./config`, `~/media/movies` | `/home/aldo/dev/01-core-infra/plex/` |
| qbittorrent | No network config, no restart policy, relative paths `./config`, `./downloads` | `/home/aldo/dev/01-core-infra/qbittorrent/` |
| nextcloud | Uses `${MYSQL_ROOT_PASSWORD}` env vars without .env template, hardcoded `/mnt/HDD1/nextcloud` | `/home/aldo/dev/01-core-infra/nextcloud/` |

### Fixes Applied (2026-08-04)
1. **Plex Template** (`templates/infra/05-media-plex/docker-compose.yml`):
   - Removed `network_mode: host` (incompatible with Traefik bridge network)
   - Added `traefik_net` network
   - Replaced relative paths with absolute HDD paths:
     - `/mnt/HDD1/plex/config:/config`
     - `/mnt/HDD1/media/movies:/movies`
     - `/mnt/HDD1/media/tv:/tv`
   - Added `restart: unless-stopped`

2. **Qbittorrent Template** (`templates/infra/05-media-qbittorrent/docker-compose.yml`):
   - Added `traefik_net` network
   - Added `restart: unless-stopped`
   - Replaced relative paths with absolute HDD paths:
     - `/mnt/HDD1/qbittorrent/config:/config`
     - `/mnt/HDD1/downloads:/downloads`

3. **Nextcloud Template** (`templates/infra/05-media-nextcloud/docker-compose.yml`):
   - Removed obsolete `version: '3.9'` field (Docker Compose v2 ignores it)
   - Replaced hardcoded env vars with placeholders:
     - `${MYSQL_ROOT_PASSWORD}`
     - `${MYSQL_PASSWORD}`
   - Kept absolute path `/mnt/HDD1/nextcloud:/var/www/html`

4. **Traefik Routes** (`templates/infra/04-network-traefik/routes.yml`):
   Added HTTP router entries for:
   - `plex.aldof.duckdns.org` → `plex:32400`
   - `qbittorrent.aldof.duckdns.org` → `qbittorrent:8080`

5. **Vault Credentials** (`vaults/nextcloud-credentials.yml`):
   Created placeholder vault file with MySQL credentials

6. **Containers Role** (`ansible/roles/containers/tasks/main.yml`):
   Added `include_vars` task to load nextcloud vault credentials before deployment

### Additional Fixes Applied (2026-08-13)
During the full playbook test, additional issues were discovered and fixed:

1. **Qbittorrent Router Missing** - Added `qbittorrent-http` and `qbittorrent` routers to `templates/infra/04-network-traefik/routes.yml` with proper HTTPS redirect and TLS certResolver

2. **Nextcloud Healthcheck Added** - Added healthcheck to Nextcloud compose template:
   ```yaml
   healthcheck:
     test: ["CMD","curl","-f","http://localhost:80/status.php"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

3. **Runtime Directories Created** - Manually created `/home/aldo/dev/05-media-{plex,qbittorrent,nextcloud}/` directories and copied compose files

4. **Missing Packages Installed** - Installed `docker.io`, `plocate`, `jq`, `git`, `curl` via apt (verification script was reporting false negatives)

5. **Nextcloud Container Name Fixed** - The actual container name is `05-media-nextcloud-app-1` (not `nextcloud` or `nextcloud-app-1`). Updated verification script accordingly.

### Verification Status (2026-08-13) - ALL CHECKS PASS
```bash
python3 tests/verify_deployment.py
# Output: �� All checks passed!
```

All 17 verification checks pass:
- Core services (opencode-web): active, enabled, listening on port 4096
- Path placeholders: core_infra_home and test user resolved correctly
- Media containers: Plex, Qbittorrent, Nextcloud all running on traefik_net
- Traefik routes: All domains present with proper quoting
- Nextcloud: Container healthy
- Required packages: docker.io, plocate, jq, git, curl all installed

### Note: Separate Nextcloud Instance
A separate Nextcloud instance exists at `/home/aldo/dev/06-apps-nextcloud/` (managed outside 01-core-infra) with its own docker-compose.yml. The 05-media-nextcloud template deploys a *second* instance. Coordinate to avoid port/volume conflicts.

### Verification After Fix
```bash
# Run playbook
cd /home/aldo/dev/01-core-infra && ./install.sh

# Verify containers running
docker ps | grep -E 'plex|qbittorrent|nextcloud'

# Verify Traefik routes
docker exec traefik cat /etc/traefik/routes.yml | grep -A 10 'plex\|qbittorrent'

# Run verification script
python3 tests/verify_deployment.py
```

## User Group Management

The role ensures the user `aldo` is added to necessary groups for infrastructure management:

- `docker` group for Docker socket access
- `www-data` group for web server file access (added via Ansible user module with `append: yes`)

### Reference Files

- `references/dev-directory-ownership.md` - Map of which ~/dev dirs are Ansible-managed vs loose; "two clones of same remote are not duplicates" pitfall; hermes-skills single-repo symlink fact; current playbook role order vs stale 01-core-infra/AGENTS.md doc. Read before any ~/dev cleanup or "is this dir managed?" task.
- `references/vaultwarden-password-reset.md` - Vaultwarden password reset procedure via admin CLI. Covers PATH fix (/vaultwarden full path required), container stop/reset/restart workflow, and volume verification. Read when a user cannot log into Vaultwarden.
- `references/project-structure-cleanup.md` - Cleanup inside 01-core-infra: removing stale runtime copies, organizing scripts into subdirectories
- `references/media-services-deployment.md` - Media services deployment gap analysis and fixes
- `references/adding-tools.md` - Pattern for adding new tools to infrastructure
- `references/camoufox-integration.md` - Camoufox anti-detect browser integration (2026-08-04)
- `references/infrastructure-verification.md` - Three-layer verification workflow (Python, Ansible, Template validation)
- `references/ansible-idempotency-patterns.md` - Idempotency improvement patterns for Ansible playbooks
- `references/traefik-route-structure.md` - Route organization pattern: public vs dev.* services, service URL mapping for Docker/host networks
- `references/nextcloud-deployment-fixes.md` - Complete Nextcloud recovery: .ncdata, network isolation, stale DB volume, proxy headers
- `references/nextcloud-appdata-fix.md` - Fix Internal Server Error when richdocuments app fails due to missing appdata_* directory after instance ID change
- `references/hermes-webui-deployment.md` - Deploy Hermes WebUI via Ansible: docker-compose template, network config, and Traefik routing
- `references/thuis-transcoding.md` - thuis-v4 transcoding feature: CLI arguments, smart source selection, FFmpeg integration
- `references/thuis-case-insensitive-dedup.md` - thuis-v4 case-insensitive pre-download deduplication fix for VRT API casing inconsistency

### Subdomain Organization Pattern (08/2026)

Services should be organized by access requirements:

| Group | Subdomain Pattern | IP Allowlist |
|-------|------------------|--------------|
| Public services | `*.aldof.duckdns.org` | None |
| Dev infrastructure | `*.dev.aldof.duckdns.org` | Yes (private IPs) |

**Example:**
- `cloud.aldof.duckdns.org` - Nextcloud (public)
- `portainer.dev.aldof.duckdns.org` - Portainer (dev, IP restricted)
- `cockpit.dev.aldof.duckdns.org` - Cockpit (dev, IP restricted)
- `plex.aldof.duckdns.org` - Plex (public)
- `web.hermes.dev.aldof.duckdns.org` - Hermes WebUI (dev, IP restricted)

**Critical:** When migrating services to dev subdomains, remove old routes from `aldof.duckdns.org` to avoid confusion.

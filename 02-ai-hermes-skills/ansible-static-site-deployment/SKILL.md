---
name: ansible-static-site-deployment
description: Deploy static sites via Ansible roles on the Pi.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [ansible, static-site, deployment, role, nginx, traefik]
---

# Ansible Static Site Deployment

Deploy static websites as Ansible roles within the `01-core-infra` infrastructure.

## When to Use

- User wants a static homepage/dashboard deployed via Ansible
- Site needs server-side metrics injected into the page
- Deployment target is the Pi infrastructure (Traefik → Nginx)

## Directory Naming Convention

**CRITICAL**: Use `~/dev/06-apps-<name>` — never bare names like `/home/aldo/dev/neo-brutalist-home`.

| Group | Pattern | Deploy Target |
|-------|---------|---------------|
| 06 | `~/dev/06-apps-<name>` | Own repo or dev dir |
| 04 | `~/dev/04-network-<name>` | Sibling repo |
| 01 | `~/dev/01-core-infra/<name>` | In-repo |

## Standard Role Structure

```
ansible/roles/<name>/
├── defaults/main.yml      # Variables with defaults
├── handlers/main.yml      # Service reload handlers
├── tasks/main.yml         # Deployment tasks
├── templates/             # Jinja2 templates
│   ├── index.html.j2
│   ├── style.css
│   ├── *.service.j2
│   ├── *.timer.j2
│   └── *.conf.j2
└── README.md
```

Also create templates in `01-core-infra/templates/infra/<name>/` for the infra layer.

## Site.yml Integration

Add to `ansible/playbooks/site.yml` roles section:

```yaml
roles:
  - "base"
  - "tools"
  - "templates"
  - "systemd"
  - "<name>"
  - "cron"
  - "mesh_sync"
```

## Standard Tasks Pattern

1. Ensure Nginx installed and running
2. Create directory structure (web root, logs, script dir)
3. Deploy static files (index.html, style.css, etc.)
4. Deploy systemd service + timer for dynamic content
5. Deploy Nginx site configuration
6. Deploy Traefik dynamic routing
7. Enable services

## Metrics Collection Pattern

For sites needing dynamic metrics:

1. Shell script reads `/proc/`, `df`, etc.
2. Outputs JSON to `/var/www/<site>/metrics.json`
3. Wrapped in systemd service + timer (60s refresh)
4. Nginx SSI or client-side fetch injects metrics
5. Handle missing sensors gracefully (show "N/A")

## Neo-Brutalist Design

- Raw HTML/CSS — no frameworks
- Bold 3px black borders, high contrast
- Monospace fonts, no rounded corners
- Server-side rendered (no JS required)
- Max 50KB uncompressed

## ⚠️ Pre-Flight Checklist (BEFORE implementing)

**ALWAYS verify these before writing deployment code:**

1. **Disk layout**: Check actual mount points and partitions
   ```bash
   df -h | grep -v tmpfs
   lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
   ```
   - Do HDD1/SSD mounts exist? Or are they on a single disk?
   - Adjust metric collection script accordingly

2. **Ansible inventory**: Check if inventory exists and has useful data
   ```bash
   cat 01-core-infra/inventories/local.yml
   ansible-inventory --list
   ```
   - If no inventory exists, subsite links must be hardcoded
   - Project count requires at least one host entry

3. **Traefik configuration**: Check if dynamic config exists
   ```bash
   find /etc/traefik -type f
   cat /etc/traefik/traefik.yml | grep -A5 providers
   ```
   - Does Traefik use file provider? Docker provider?
   - Is there a `dynamic` directory for router configs?

4. **Nginx status**: Check if Nginx is installed
   ```bash
   ls /etc/nginx/sites-enabled/
   systemctl status nginx
   ```
   - If not installed, Ansible role must install it
   - If installed, avoid removing the default site without replacement

5. **CPU temperature path**: Verify thermal zones exist
   ```bash
   ls /sys/class/thermal/thermal_zone*/temp
   ls /sys/class/hwmon/hwmon*/temp*_input
   ```
   - Different paths may exist on different hardware

## Pitfalls

- **ARM64 packages**: Rust MCP servers may lack ARM64 builds. Use TypeScript alternatives.
- **npx piping**: Unreliable for smoke tests. Use Python MCP SDK client.
- **`--connect-timeout` placement**: Must come BEFORE `--args` in `hermes mcp add`.
- **Template paths**: Use `{{ __CORE_INFRA__ }}`, not hardcoded paths.
- **Pre-flight missing**: Always check disk layout, inventory, Traefik config before implementation.
- **Template location**: Templates go in `01-core-infra/templates/infra/`, not in the project folder.
- **Directory naming**: Must use `~/dev/06-apps-<name>` pattern, never bare names.

## References

- `references/pre-flight-checklist.md` — Environment verification before implementation.

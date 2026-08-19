# Neo-Brutalist Homepage Specification

## Project: 06-apps-neo-brutalist-home

### Overview

A neo-brutalist-styled static homepage served at `aldof.duckdns.org` that displays real-time server metrics and links to all deployed subsites. The page is built with raw HTML and CSS (no frameworks, no JavaScript required for core content). All deployment is managed via Ansible from the `01-core-infra` repository.

---

## Requirements

### 1. Visual Design (Neo-Brutalist)

- **Raw HTML/CSS only** — no frameworks, no build tools, no JavaScript frameworks
- **Bold borders** — thick, solid, high-contrast borders on all containers
- **High contrast** — black text on white/cream background, or inverted
- **Monospace fonts** — system monospace for headings and code elements
- **Unpolished aesthetic** — visible grid lines, raw edges, no rounded corners
- **Semantic HTML** — proper heading hierarchy, `<main>`, `<nav>`, `<section>`, `<footer>`
- **Responsive** — works on mobile (320px) and desktop (1920px+)
- **Max page weight**: 50KB uncompressed (no external dependencies)

### 2. System Metrics Display

All metrics are collected server-side and injected into the HTML at render time.

| Metric | Source | Format | Refresh |
|--------|--------|--------|---------|
| **Uptime** | `/proc/uptime` + `uptime -p` | Human-readable (e.g., "47 days, 3h 22m") | 60s |
| **RAM** | `/proc/meminfo` | Used / Total (GB), percentage bar | 60s |
| **HDD1** | `df -h /` or `df -h /mnt/hdd1` | Used / Total (GB), percentage bar | 60s |
| **SSD** | `df -h /mnt/ssd` or `df -h /` for NVMe | Used / Total (GB), percentage bar | 60s |
| **CPU Load** | `/proc/loadavg` | 1m, 5m, 15m load averages | 60s |
| **CPU Temp** | `cat /sys/class/thermal/thermal_zone0/temp` | Degrees Celsius | 60s |

### 3. Project Counter

- Count all active Ansible inventory hosts/groups that represent deployed projects
- Source: `ansible-inventory --list` from `01-core-infra/inventories/local.yml`
- Display: "N projects deployed" with a breakdown by group

### 4. Subsite Links

- Auto-generated from Ansible inventory `group_vars` and `host_vars`
- Each subsite gets a card with:
  - Name (from inventory)
  - URL (from inventory variable `site_url` or derived from group)
  - Status indicator (green dot = reachable, red = unreachable)
  - Last checked timestamp
- Ordered alphabetically by subsite name

### 5. Deployment

- **Ansible playbook**: `01-core-infra/ansible/playbooks/site.yml`
- **Target**: `aldof.duckdns.org` via Traefik reverse proxy
- **Method**: `ansible-copy` from `templates/infra/06-apps-neo-brutalist-home/`
- **Web server**: Nginx serving static files from `/var/www/06-apps-neo-brutalist-home/`
- **Traefik route**: `Host('aldof.duckdns.org')` → Nginx backend
- **Idempotent**: Re-running the playbook produces the same result

### 6. Metrics Refresh

- **systemd timer**: `06-apps-neo-brutalist-home-metrics.timer`
- **Schedule**: Every 60 seconds (`OnUnitActiveSec=60s`, `Persistent=true`)
- **Service**: `06-apps-neo-brutalist-home-metrics.service` runs the collection script
- **Script**: `/opt/06-apps-neo-brutalist-home/collect-metrics.sh` → writes JSON to `/var/www/06-apps-neo-brutalist-home/metrics.json`
- **Nginx config**: Serves `metrics.json` and includes it in the HTML via SSI or server-side include

### 7. File Structure

```
06-apps-neo-brutalist-home/
├── .specify/
│   └── memory/
│       └── constitution.md
├── commands/
│   ├── speckit.constitution.md
│   ├── speckit.specify.md
│   ├── speckit.plan.md
│   ├── speckit.tasks.md
│   └── speckit.implement.md
├── templates/
│   └── infra/
│       └── 06-apps-neo-brutalist-home/
│           ├── ansible/
│           │   └── playbooks/
│           │   └── roles/
│           ├── nginx/
│           │   └── 06-apps-neo-brutalist-home.conf
│           ├── systemd/
│           │   ├── 06-apps-neo-brutalist-home-metrics.service
│           │   └── 06-apps-neo-brutalist-home-metrics.timer
│           └── html/
│               ├── index.html
│               ├── metrics.json
│               └── style.css
├── ansible/
│   └── playbooks/
│       └── site.yml
└── README.md
```

### 8. Non-Functional Requirements

- **No external CDN**: All CSS is inline or local
- **No JavaScript**: Core metrics work without JS (server-side rendering)
- **Graceful degradation**: If a metric collection fails, show "N/A" for that metric
- **Security**: No sensitive data exposed in metrics (no API keys, no tokens)
- **Logging**: Metrics collection logs to `/var/log/06-apps-neo-brutalist-home/metrics.log`
- **Error handling**: If Nginx is down, systemd service restarts it

---

## Design Decisions

1. **Server-side rendering over client-side JS** — The page must work without JavaScript. Metrics are collected by a shell script and injected into the HTML at build/render time.
2. **Neo-brutalist CSS only** — No Tailwind, no Bootstrap, no custom framework. A single `style.css` file with raw, bold styling.
3. **systemd timer over cron** — Consistent with the project's use of systemd for other services. The timer is persistent and survives reboots.
4. **Ansible for all deployment** — Consistent with the `01-core-infra` methodology. All configuration is in templates, deployed via `ansible-copy`.
5. **Traefik for routing** — The existing Traefik setup at `04-network-traefik` handles SSL termination and routing. The homepage gets a simple HTTP route.

---

## Acceptance Criteria

1. ✅ Page loads at `aldof.duckdns.org` with neo-brutalist styling
2. ✅ Uptime displayed in human-readable format
3. ✅ RAM usage shown with used/total and percentage
4. ✅ HDD1 usage shown with used/total and percentage
5. ✅ SSD usage shown with used/total and percentage
6. ✅ CPU load averages (1m, 5m, 15m) displayed
7. ✅ CPU temperature displayed in Celsius
8. ✅ Project count displayed
9. ✅ Subsite links auto-generated from inventory, ordered alphabetically
10. ✅ Metrics refresh every 60 seconds
11. ✅ Page works without JavaScript
12. ✅ Ansible playbook is idempotent
13. ✅ Page weight under 50KB uncompressed
14. ✅ Responsive on mobile (320px) and desktop (1920px+)
15. ✅ No external CDN dependencies

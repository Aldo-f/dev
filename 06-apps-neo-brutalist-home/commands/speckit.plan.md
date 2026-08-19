# Neo-Brutalist Homepage — Implementation Plan (Final)

## Project: 06-apps-neo-brutalist-home

### Implementation Steps

#### Phase 0: Directory Rename
0. Rename `~/dev/neo-brutalist-home/` to `~/dev/06-apps-neo-brutalist-home/`
   ```bash
   mv ~/dev/neo-brutalist-home ~/dev/06-apps-neo-brutalist-home
   ```

#### Phase 1: Infrastructure Setup
1. Mount 18TB HDD at `/mnt/HDD1` (already ext4 formatted)
2. Create `templates/infra/06-apps-neo-brutalist-home/` with all Ansible roles and templates
3. Create `ansible/playbooks/site.yml` for deployment orchestration
4. Create systemd service and timer units for metrics collection
5. Create metrics collection shell script
6. Create Nginx configuration for static file serving (port 8080)
7. Create Traefik route configuration for `aldof.duckdns.org`

#### Phase 2: Homepage Development
8. Write `index.html` — semantic HTML5 with neo-brutalist styling
9. Write `style.css` — raw CSS with bold borders, high contrast, monospace fonts
10. Write `metrics.json` template — JSON structure for dynamic metric injection
11. Write `collect-metrics.sh` — shell script to gather system metrics
12. Integrate metrics into HTML via JavaScript fetch (no SSI required)

#### Phase 3: Ansible Deployment
13. Create Ansible role `neo-brutalist-home` with tasks for:
    - Installing Nginx
    - Deploying static files
    - Deploying systemd units
    - Configuring Traefik route (appends to existing routes.yml)
    - Enabling and starting services
14. Add role to `01-core-infra/ansible/playbooks/site.yml`
15. Test idempotency (run playbook twice, verify no changes on second run)

#### Phase 4: Verification
16. Deploy to production (aldof.duckdns.org)
17. Verify subsite links are hardcoded and ordered alphabetically
18. Verify metrics refresh every 60 seconds
19. Verify page works with and without JavaScript
20. Verify responsive design on mobile and desktop
21. Verify page weight under 50KB
22. Test HTTPS at `https://aldof.duckdns.org`

---

## Detailed Task Breakdown

### Task 1: HDD Mount
```bash
# Already mounted at /mnt/HDD1 (ext4, 17TB total, 1.8TB used)
echo '/dev/sda1 /mnt/HDD1 ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
```

### Task 2: Systemd Timer and Service
Create `06-apps-neo-brutalist-home-metrics.service`:
- Type: oneshot
- ExecStart: `/opt/06-apps-neo-brutalist-home/collect-metrics.sh`
- User: root

Create `06-apps-neo-brutalist-home-metrics.timer`:
- OnUnitActiveSec: 60s
- Persistent: true
- Unit: 06-apps-neo-brutalist-home-metrics.service

### Task 3: Metrics Collection Script
`/opt/06-apps-neo-brutalist-home/collect-metrics.sh`:
- Reads `/proc/uptime` → uptime in human-readable format (e.g., "up 3 hours, 36 minutes")
- Reads `/proc/meminfo` → RAM used/total
- Runs `df -h /mnt/HDD1` for HDD1 usage
- Runs `df -h /` for SSD (root) usage
- Reads `/proc/loadavg` → CPU load averages
- Reads `/sys/class/thermal/thermal_zone0/temp` → CPU temp
- Counts subsites from `/etc/traefik/routes.yml`
- Outputs JSON to `/var/www/06-apps-neo-brutalist-home/metrics.json`
- Logs to `/var/log/06-apps-neo-brutalist-home/metrics.log`

### Task 4: Nginx Configuration
- Listen on port 8080 (internal only)
- Serve static files from `/var/www/06-apps-neo-brutalist-home/`
- No SSI needed — JavaScript fetches metrics.json
- Listen on port 80 (Traefik handles SSL)
- Server name: `aldof.duckdns.org`

### Task 5: Traefik Route
- Append to existing `/home/aldo/dev/04-network-traefik/routes.yml`
- Router: `homepage` (HTTPS) + `homepage-http` (HTTP redirect)
- Rule: `Host('aldof.duckdns.org')`
- Service: `homepage` (Nginx on 127.0.0.1:8080)
- TLS: certResolver: myresolver

### Task 6: Ansible Role
Role: `neo-brutalist-home`
Tasks:
1. Install Nginx (idempotent, check if already installed)
2. Create `/var/www/06-apps-neo-brutalist-home/` directory
3. Deploy `index.html` from template
4. Deploy `style.css` from template
5. Deploy `collect-metrics.sh` from template
6. Deploy `metrics.json` from template
7. Deploy systemd service and timer files
8. Deploy Nginx configuration
9. Append Traefik route to routes.yml
10. Enable and start systemd timer
11. Enable and start Nginx
12. Reload Traefik configuration

### Task 7: HTML Template
`index.html` — semantic HTML5:
- `<header>` with site title and last updated timestamp
- `<main>` with sections:
  - System Metrics (uptime, RAM, HDD1, SSD, CPU load, CPU temp)
  - Project Counter (subsite count from routes.yml)
  - Subsite Links (hardcoded, ordered alphabetically)
- `<footer>` with deployment info
- All metrics fetched via JavaScript fetch() from metrics.json

### Task 8: CSS Template
`style.css` — neo-brutalist styling:
- Font: system monospace (`'Courier New', monospace`)
- Background: white or cream (`#f5f5f0`)
- Text: black (`#000000`)
- Borders: 3px solid black on all containers
- Headings: bold, uppercase, monospace
- Links: black with underline, bold on hover
- Cards: white background, black border, padding
- Grid layout for metrics display
- Responsive breakpoints at 768px and 1024px

---

## Updated File Structure

```
~/dev/06-apps-neo-brutalist-home/           # Spec-kit project (metadata only)
├── .specify/memory/constitution.md
├── commands/speckit.specify.md
├── commands/speckit.plan.md
└── README.md

01-core-infra/
├── templates/infra/06-apps-neo-brutalist-home/
│   ├── html/index.html                      # Homepage HTML
│   ├── html/style.css                       # Neo-brutalist CSS
│   ├── nginx/neo-brutalist-home.conf.j2     # Nginx config (port 8080)
│   ├── systemd/collect-metrics.sh.j2        # Metrics collection script
│   ├── systemd/neo-brutalist-home-metrics.service.j2
│   ├── systemd/neo-brutalist-home-metrics.timer.j2
│   └── traefik/neo-brutalist-home.toml.j2   # Traefik route config
├── ansible/roles/neo-brutalist-home/
│   ├── defaults/main.yml
│   ├── handlers/main.yml
│   ├── tasks/main.yml
│   └── templates/ (*.j2, style.css)
└── ansible/playbooks/site.yml               # neo-brutalist-home role added
```

---

## Dependencies

- Ansible >= 2.15
- Nginx (installed by Ansible)
- Traefik (already deployed at `04-network-traefik` with file provider)
- systemd (already present on Pi)
- `spec-kit-mcp` (already registered in Hermes)
- `/dev/sda1` mounted at `/mnt/HDD1` (17TB ext4)

## Risks

- CPU temperature path may differ on Pi 5 (`/sys/class/thermal/thermal_zone0/temp` vs `/sys/class/hwmon/hwmon0/temp`)
- Traefik route append uses `lineinfile` — must not duplicate on re-run
- Metrics collection script must handle missing sensors gracefully (show "N/A")
- HDD mount point `/mnt/HDD1` must exist before metrics collection

## Success Criteria

1. ✅ Page loads at `https://aldof.duckdns.org` with correct neo-brutalist styling
2. ✅ Uptime displayed in human-readable format
3. ✅ RAM usage shown with used/total and percentage
4. ✅ HDD1 usage shown with used/total and percentage (17TB)
5. ✅ SSD (root) usage shown with used/total and percentage (238GB)
6. ✅ CPU load averages (1m, 5m, 15m) displayed
7. ✅ CPU temperature displayed in Celsius
8. ✅ Subsite count displayed (derived from routes.yml)
9. ✅ Subsite links hardcoded and ordered alphabetically
10. ✅ Metrics refresh every 60 seconds
11. ✅ Page works with and without JavaScript
12. ✅ Ansible playbook is idempotent
13. ✅ Page weight under 50KB uncompressed
14. ✅ Responsive on mobile (320px) and desktop (1920px+)
15. ✅ HTTPS works via Traefik Let's Encrypt
16. ✅ No external CDN dependencies

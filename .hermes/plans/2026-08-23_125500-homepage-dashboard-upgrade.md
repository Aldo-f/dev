# Homepage Dashboard Upgrade — Implementation Plan

**Goal:** Turn aldof.duckdns.org (gethomepage v1.13.2) into a complete ops dashboard: every container as a live card, Pi5 + Pi3 hardware metrics (uptime, CPU temp, RAM, disk incl. 17 TB HDD1), Portainer widget, portfolio bookmark.

**Architecture:** Zero new containers on the Pi5 side. Native Glances v4 (web mode, systemd) on **both** Pis; homepage consumes them via info widgets. Docker integration enabled over the already-mounted read-only socket. All dashboard config lives in git-tracked `~/dev/06-apps-neo-brutalist-home/config/*.yaml`; homepage hot-reloads YAML (no restart needed for services/widgets).

**Tech Stack:** gethomepage v1.13.2 · glances 4.5.6 (`uv tool`, systemd) on Pi5 · glances (apt, Debian 13) on Pi3 · Traefik routes unchanged.

---

## Verified context (do not re-litigate)

| Fact | Value |
|---|---|
| This host | **pi5 = 192.168.0.5**, hostname `pi5` |
| Homepage | container `homepage`, `ghcr.io/gethomepage/homepage:v1.13.2`, port 3000, root user, docker.sock mounted `:ro` |
| Config dir (live + git-tracked) | `~/dev/06-apps-neo-brutalist-home/config/` |
| Compose source | `~/dev/01-core-infra/templates/infra/06-apps-neo-brutalist-home/docker-compose.yml` (Ansible-managed; runtime project dir `/workspace/06-apps-neo-brutalist-home`) |
| HDD1 | 17 TB mounted `/mnt/HDD1` (8% used) |
| Pi3 | **192.168.0.3** (MAC b8:27:eb…, SSH up, OpenSSH Debian 13; I have no credentials — Aldo runs the commands) |
| Pi3 existing service | Hermes metrics dashboard :9119 |
| Portainer UI | https://portainer.dev.aldof.duckdns.org (LAN+home-IP allowlisted), local :9000 |
| Glances latest stable | 4.5.6 |
| Kanban ticket | `t_a362b3b1` |

**Decisions taken (user):** lightweight plan doc (this file), then implement; Pi3 handled by handing Aldo exact commands; all containers visible; Portainer widget wanted (key pending).

---

## Task 1: Enable Docker integration

**Files:** Modify `~/dev/06-apps-neo-brutalist-home/config/docker.yaml`

Replace whole file with:

```yaml
# For configuration options and examples, please see:
# https://gethomepage.dev/configs/docker/

pi5:
  socket: /var/run/docker.sock
```

**Verify:** homepage picks it up within seconds — `docker logs homepage --tail 20 2>&1 | grep -i error` stays quiet; later tasks reference `server: pi5`.

## Task 2: Glances 4.5.6 in web mode on the Pi5 (this host)

**Files:** Modify `~/dev/01-core-infra/templates/systemd/glances-web.service` (new template), then deploy via the passwordless-sudo helper `app-deploy-systemd`.

**Step 1:** Install pinned glances (PEP 668 → use uv, no sudo):

```bash
uv tool install 'glances==4.5.6'
~/.local/bin/glances --version   # expect: Glances v4.5.6
```

**Step 2:** Create systemd template `templates/systemd/glances-web.service` (use `__HOME__`/`__USER__` macros, never `/home/aldo`):

```ini
[Unit]
Description=Glances web server (homepage metrics)
After=network-online.target

[Service]
User=__USER__
ExecStart=__HOME__/.local/bin/glances -w -p 61208 --disable-plugin docker
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Step 3:** Deploy + start:

```bash
app-deploy-systemd glances-web.service __HOME__/.local/bin/glances -w -p 61208 --disable-plugin docker
systemctl status glances-web --no-pager | head -5
```

(Exact helper invocation per its man page; fallback: `systemctl enable --now` after placing the unit with rendered paths.)

**Step 4: Verify (real runtime):**

```bash
curl -s http://127.0.0.1:61208/api/4/uptime
curl -s http://127.0.0.1:61208/api/4/sensors/topic/temperature | head -c 200
curl -s http://127.0.0.1:61208/api/4/fs | python3 -m json.tool | grep -A2 HDD1
```

Expect: uptime string; temperature JSON; `/mnt/HDD1` present. Port stays LAN-only — nothing added to Traefik.

---

## Task 3: Glances on the Pi3 (192.168.0.3) — commands handed to Aldo

I have no SSH credentials for the Pi3. Hand Aldo this exact block to run there:

```bash
ssh <user>@192.168.0.3 '
sudo apt-get update && sudo apt-get install -y glances
glances --version
sudo tee /etc/systemd/system/glances-web.service >/dev/null <<EOF
[Unit]
Description=Glances web server
After=network-online.target

[Service]
ExecStart=/usr/bin/glances -w -p 61208 --disable-plugin docker
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now glances-web
'
# back on the Pi5, verify reachability:
curl -s http://192.168.0.3:61208/api/4/uptime
curl -s http://192.168.0.3:61208/api/4/sensors/topic/temperature
```

**Verify from Pi5:** both curls return data. If the Pi3 has no temperature sensor (common on Pi3 without `cpu_thermal` exposed), the widget still shows CPU/RAM/disk/uptime — temp field simply won't render.

## Task 4: Full `services.yaml` — every container as a live card

**Files:** Rewrite `~/dev/06-apps-neo-brutalist-home/config/services.yaml`

```yaml
# https://gethomepage.dev/configs/services/
- Proxy & Network:
    - Traefik:
        icon: traefik-proxy.png
        description: Reverse proxy (:80/:443)
        server: pi5
        container: traefik
    - Portainer:
        icon: portainer.png
        href: https://portainer.dev.aldof.duckdns.org
        description: Container management
        server: pi5
        container: portainer
    - Cockpit:
        icon: cockpit-project.png
        href: https://cockpit.dev.aldof.duckdns.org
        description: Host management
        server: pi5
        container: cockpit

- Media:
    - Jellyfin:
        icon: jellyfin.png
        href: https://jellyfin.aldof.duckdns.org
        description: Media server
        server: pi5
        container: jellyfin
    - qBittorrent:
        icon: qbittorrent.png
        href: https://qbittorrent.aldof.duckdns.org
        description: Downloads
        server: pi5
        container: qbittorrent

- AI:
    - FreeLLM API:
        icon: si-openai-#412991
        href: https://freellm.aldof.duckdns.org
        description: LLM API gateway
        server: pi5
        container: 02-ai-freellmapi-freellmapi-1
    - Hermes WebUI:
        icon: mdi-robot-outline
        href: https://web.hermes.dev.aldof.duckdns.org
        description: Hermes agent chat
        server: pi5
        container: hermes-webui
    - Hermes TQ:
        icon: mdi-checkbox-marked-circle-outline
        href: https://tq.hermes.dev.aldof.duckdns.org
        description: Kanban board
        server: pi5
        container: hermes-tq

- Files & Vault:
    - Nextcloud:
        icon: nextcloud.png
        href: https://cloud.aldof.duckdns.org
        description: Files & sync
        server: pi5
        container: nextcloud
    - MariaDB (NC):
        icon: mariadb.png
        description: Nextcloud database
        server: pi5
        container: nextcloud-db
    - Redis (NC):
        icon: redis.png
        description: Nextcloud cache/locking
        server: pi5
        container: nextcloud-redis
    - Vaultwarden:
        icon: vaultwarden.png
        href: https://vault.aldof.duckdns.org
        description: Password vault
        server: pi5
        container: vaultwarden

- Apps:
    - Stantonius:
        icon: church.png
        href: https://stantonius.aldof.duckdns.org
        description: WordPress site
        server: pi5
        container: stantonius-web
    - MariaDB (Stantonius):
        icon: mariadb.png
        description: WordPress database
        server: pi5
        container: stantonius-db
    - Toerekening:
        icon: mdi-calculator-variant-outline
        href: http://192.168.0.5:3002
        description: Rekenapp
        server: pi5
        container: 06-apps-toerekening-toerekening-1
    - PINO:
        icon: mdi-cash-multiple
        href: http://192.168.0.5:4747
        description: Passive income orchestrator
        server: pi5
        container: pino_server
    - Clocky:
        icon: mdi-clock-digital
        href: https://clock.dev.aldof.duckdns.org
        description: Clock app
        server: pi5
        container: clocky

- Dashboard:
    - Homepage:
        icon: homepage.png
        href: https://aldof.duckdns.org
        description: This dashboard
        server: pi5
        container: homepage
    - Portfolio:
        icon: sh-github
        href: https://aldo-f.github.io/
        description: aldo-f.github.io
```

Notes: `server:`/`container:` give status dot + click-to-expand CPU/RAM/net per card (socket already mounted `:ro`, container runs as root). Cards without `href` (Traefik, DBs) still show live status/stats. Portfolio bookmark lives here rather than bookmarks.yaml so it sits with the cards.

**Verify:** reload aldof.duckdns.org in browser → all groups render, status dots green within ~30 s, clicking a dot expands stats.

## Task 5: `widgets.yaml` — info widgets for both Pis + Portainer

**Files:** Rewrite `~/dev/06-apps-neo-brutalist-home/config/widgets.yaml`

```yaml
# https://gethomepage.dev/widgets/
- glances:
    label: pi5
    url: http://192.168.0.5:61208
    version: 4
    cpu: true
    mem: true
    cputemp: true
    uptime: true
    disk:
      - /
      - /mnt/HDD1

- glances:
    label: pi3
    url: http://192.168.0.3:61208
    version: 4
    cpu: true
    mem: true
    cputemp: true
    uptime: true
    disk: /
```

Notes:
- Glances v4 → `version: 4` is required.
- `cputemp`/`uptime`/`disk` are off by default — explicitly enabled; `cpuSensorLabel` only if temp doesn't show (Pi5 sensor label usually matches `cpu_thermal`).
- Portainer is a **service** widget (docs: widgets/services/portainer) — it attaches to the Portainer **card** in Task 6, NOT here.

**Verify (before Portainer key):** dashboard top bar shows two labeled glances blocks with uptime/temp/disk values matching `curl http://127.0.0.1:61208/api/4/uptime`.

## Task 6: Portainer service widget (blocked on Aldo's API key)

**Files:** Modify the Portainer entry in `services.yaml` (Task 4) — add a `widget:` block:

```yaml
    - Portainer:
        icon: portainer.png
        href: https://portainer.dev.aldof.duckdns.org
        description: Container management
        server: pi5
        container: portainer
        widget:
          type: portainer
          url: http://192.168.0.5:9000
          env: 1   # environment ID — confirm in Portainer URL after clicking the environment (#!/endpoints/1 → 1)
          key: <PTR_... API key from Aldo>
          fields: ["running", "stopped", "total"]
```

Key generation (Aldo, ~30 s): Portainer UI → top-right **Account settings** → **API keys** → *Add key* → copy `ptr_...`.

**Verify:** Portainer card shows live running/stopped/total counts.

---

## Task 7: Commit + end-to-end evidence

**Files:** git commit in `~/dev` (single root; config dir is tracked).

1. `git add 06-apps-neo-brutalist-home/config/ 01-core-infra/templates/systemd/glances-web.service`
2. Commit `feat(homepage): full container grid, glances metrics pi5+pi3, portainer widget` and push.
3. Close kanban `t_a362b3b1`: `hermes kanban complete t_a362b3b1 --result "<evidence summary>"`

**Final verification (all must pass against the LIVE site):**

```bash
curl -sk -o /dev/null -w '%{http_code}\n' https://aldof.duckdns.org/                 # 200
curl -s http://127.0.0.1:61208/api/4/uptime                                          # pi5 uptime
curl -s http://192.168.0.3:61208/api/4/uptime                                        # pi3 uptime
curl -sk https://aldof.duckdns.org/ | grep -c 'status-dot\|Jellyfin\|Nextcloud'      # cards rendered server-side count > 0
docker logs homepage --tail 40 2>&1 | grep -ci error                                 # 0 new errors
```

Plus one browser screenshot of aldof.duckdns.org as visual proof.

---

## Risks / notes

- **Config drift:** Ansible manages only this service's compose file, not `config/*.yaml` — edits persist. Template copies under `01-core-infra/templates/.../config/` are stale samples; Task 7 syncs or removes them to prevent confusion.
- **Pi3 temp sensor:** may not expose CPU temp; widget degrades gracefully.
- **Glances v4 API:** homepage needs `version: 4` — forgetting it yields empty widgets.
- **Port 61208 exposure:** stays LAN-only on both hosts; nothing routed through Traefik. Pi3 firewall must allow 61208 from LAN.
- **Rollback:** all changes are YAML files in git + one systemd unit; `git checkout` + `systemctl disable --now glances-web` reverts everything.

## Open questions

1. Pi3 SSH username/password (only needed if Aldo prefers I drive the install via an interactive path).
2. Portainer environment ID + API key (Task 6 unblocks the moment they arrive).

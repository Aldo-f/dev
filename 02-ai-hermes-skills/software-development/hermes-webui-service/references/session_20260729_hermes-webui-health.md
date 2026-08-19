## Session 2026‑07‑29 – Hermes WebUI health verification after manual reboot

The following commands were executed to confirm that the Hermes WebUI was running and healthy on the Raspberry Pi (IP 192.168.0.5) after a manual reboot. The WebUI is managed via the repository's `ctl.sh` script, not a systemd unit.

```bash
# Verify the Python process is alive
ps -ef | grep -i hermes | grep -v grep
#> aldo 11547 1 4 Jul28 ? 00:11:59 /home/aldo/.hermes/hermes-agent/venv/bin/python /home/aldo/dev/02-ai-hermes-webui/server.py
```

```bash
# Check listening socket
ss -tlnp | grep :8787
#> LISTEN 0 64 0.0.0.0:8787 0.0.0.0:* users:("python",pid=11547,fd=6)
```

```bash
# Service status via ctl.sh
./ctl.sh status
#> ● hermes-webui — running
#>   PID: 11547
#>   Uptime: 04:12:46
#>   Bound: 0.0.0.0:8787
#>   Log: /home/aldo/.hermes/webui.log
#>   Health: ok (11 sessions, 3 active streams)
```

```bash
# Health endpoint JSON
curl -s http://192.168.0.5:8787/health
#> { "status": "ok", "sessions": 11, "active_streams": 3, "active_runs": 3, ... }
```

```bash
# Base URL reachable from LAN (302 redirect to sign‑in page)
curl -s -L -w "%{http_code}" http://192.168.0.5:8787/ -o /dev/null
#> 200
```

**Key take‑aways**
- The UI does **not** survive a reboot; after a reboot you must run `./ctl.sh start` again.
- No systemd unit exists (`app-hermes-webui.service` is not provided). Use the `ctl.sh` script for lifecycle management.
- Ensure `HERMES_WEBUI_HOST=0.0.0.0` in `.env` to allow LAN access.
- Logs are at `${HOME}/.hermes/webui.log` and are useful for diagnosing crashes.

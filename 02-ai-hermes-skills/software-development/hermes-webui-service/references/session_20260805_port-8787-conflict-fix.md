# Session 2026-08-05: Port 8787 Conflict Fix for Hermes WebUI

## Problem
- HTTPS endpoint `https://web.hermes.dev.aldof.duckdns.org/` returned 502 Bad Gateway
- Port 8787 was occupied by a stale Python process (`/home/aldo/.hermes/hermes-agent/venv/bin/python /home/aldo/dev/02-ai-hermes-webui/server.py`, PID 1199)
- This prevented the Docker container from starting (bind: address already in use)

## Root Cause
A manually started `server.py` process (outside Docker) was holding port 8787, blocking the Docker container managed by `docker compose`.

## Resolution
```bash
# 1. Identify the process holding port 8787
ss -tlnp | grep 8787

# 2. Kill the stale process
kill <PID>

# 3. Start the Docker container
docker compose -f /home/aldo/dev/02-ai-hermes-webui/docker-compose.yml up -d hermes-webui

# 4. Verify HTTPS accessibility
curl -s -I https://web.hermes.dev.aldof.duckdns.org/ | grep "200 OK"
```

## Prevention
- Always use Docker Compose for production deployments
- After system changes, verify no stale processes: `ss -tlnp | grep 8787`
- The Docker Compose file has `restart: unless-stopped` for automatic recovery

## Related
- Traefik routes.yml correctly configured with `hermes-webui` service pointing to `http://127.0.0.1:8787`
- WebUI Docker Compose binds to `127.0.0.1:8787:8787`
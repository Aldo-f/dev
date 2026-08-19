# Debugging Session: Traefik 404 for freellm.aldof.duckdns.org
# Date: 2026-08-01
# Duration: ~17 minutes

## Problem
- HTTPS 404 Not Found on https://freellm.aldof.duckdns.org
- HTTP 200 on http://127.0.0.1:3001 from host
- Container healthy, port mapping correct

## Root Causes
1. **Corrupted routes.yml structure**: User's manual edits left duplicate keys, invalid YAML fragments (leftover from incomplete edits)
2. **Docker DNS resolution failure**: Traefik couldn't resolve `freellmapi` hostname despite both containers on same network
3. **freellmapi binds to 127.0.0.1**: Container default HOST_BIND was localhost, unreachable from sibling containers
4. **Traefik file provider reload unreliable**: `docker compose restart` didn't pick up new config, needed `down/up`

## Diagnostic Commands
```bash
# Check Traefik logs for YAML errors
docker logs traefik --tail 20
# Look for: "field not found, node: rule" or "yaml: line X: did not find expected key"

# Verify containers on same network
docker inspect 02-ai-freellm-freellmapi-1 -f '{{range .NetworkSettings.Networks}}{{.NetworkID}}:{{.IPAddress}}{{end}}'
docker inspect traefik -f '{{range .NetworkSettings.Networks}}{{.NetworkID}}:{{.IPAddress}}{{end}}'

# Test DNS resolution from Traefik
docker exec traefik getent hosts freellmapi

# Check routes.yml syntax
docker exec traefik cat /etc/traefik/routes.yml

# Restart Traefik fully (not just restart)
cd ~/dev/04-network-traefik && docker compose down && docker compose up -d
```

## Final Fix
1. Clean routes.yml: proper `http:` structure, `rule` only in routers (not middlewares)
2. Service URL: use host IP `http://192.168.0.5:3001` instead of container name
3. freellmapi environment: set `HOST_BIND=0.0.0.0` so it listens on all interfaces
4. Traefik: full `down/up` cycle instead of restart
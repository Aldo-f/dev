# Hermes WebUI Deployment via Ansible

## Overview
Hermes WebUI is deployed via Ansible playbook in `01-core-infra`. The service runs on port 8787 and is accessible at `web.hermes.dev.aldof.duckdns.org`.

## Template Location
```
templates/infra/02-ai-hermes-webui/docker-compose.yml
```

## Key Configuration

### Docker Compose Template
```yaml
services:
  hermes-webui:
    build:
      context: /home/aldo/dev/02-ai-hermes-webui
      dockerfile: Dockerfile
    container_name: hermes-webui
    restart: unless-stopped
    expose:
      - "8787"
    networks:
      - traefik_net
    volumes:
      - /home/aldo/.hermes:/home/hermeswebui/.hermes
      - /home/aldo/workspace:/workspace
    environment:
      - HERMES_WEBUI_HOST=0.0.0.0
      - HERMES_WEBUI_PORT=8787
      - HERMES_WEBUI_STATE_DIR=/home/hermeswebui/.hermes/webui
      - HERMES_WEBUI_PASSWORD=${HERMES_WEBUI_PASSWORD}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8787/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

networks:
  traefik_net:
    external: true
```

### Container Service Registration
Add to `ansible/roles/containers/defaults/main.yml`:
```yaml
  # 02-ai-* -> AI services
  - name: 02-ai-hermes-webui
    runtime_dir: "/home/aldo/dev/02-ai-hermes-webui"
```

> **Note**: The runtime_dir points to the **source repo** (not a copy under 01-core-infra) because the Dockerfile uses `COPY . /apptoo` and the compose file uses `build: context: /home/aldo/dev/02-ai-hermes-webui`. This is correct.

### Traefik Route
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

## Service URL
- **Internal (Docker network):** `http://hermes-webui:8787`
- **External:** `https://web.hermes.dev.aldof.duckdns.org`

## Critical: Container Name Routing
**Always use Docker container names (`http://hermes-webui:8787`) instead of hardcoded host IPs (`http://192.168.0.5:8787`) in Traefik routes for services on the shared `traefik_net` network.**

### Why:
- Traefik runs on `traefik_net` and resolves container names via Docker's internal DNS
- Hardcoded IPs break when host IP changes (DHCP, static IP reconfiguration)
- Container name resolution is stable and doesn't require external routing

## Common Issues

### Port Already in Use
If `./ctl.sh start` fails with "live server already responding on 127.0.0.1:8787", the service is running outside Docker (direct Python). Kill the process and restart via Docker.

### Health Check Failing
The health check uses `curl` inside the container. If the service starts but health check fails, wait for startup (20s start_period) before testing.

### Traefik Can't Reach Service
If Traefik returns 502 Bad Gateway:
1. Verify both containers are on `traefik_net`: `docker network inspect traefik_net`
2. Test DNS resolution from Traefik: `docker exec traefik wget -qO- http://hermes-webui:8787/health`
3. Check Traefik routes: `docker exec traefik cat /etc/traefik/routes.yml | grep -A3 hermes-webui`
4. Ensure route uses container name, not host IP

## Verification
```bash
# Check container status
docker ps | grep hermes-webui

# Test health endpoint (direct)
curl -s http://localhost:8787/health

# Test health endpoint (via Traefik container)
docker exec traefik wget -qO- http://hermes-webui:8787/health

# Test external access (from internal network)
curl -I https://web.hermes.dev.aldof.duckdns.org

# Test external access via Traefik HTTPS
curl -k -H "Host: web.hermes.dev.aldof.duckdns.org" https://localhost/health
```

## Related References
- `references/traefik-route-structure.md` - Full Traefik route patterns including container name routing
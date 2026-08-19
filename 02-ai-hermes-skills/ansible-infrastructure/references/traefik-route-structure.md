# Traefik Route Structure Pattern

## Route Organization

Separate public services from infrastructure (dev.*) services with different middleware:

```yaml
# Public services (no IP allowlist)
freellm:
  rule: "Host(`freellm.aldof.duckdns.org`)"
  middlewares:
    - https-redirect
  service: freellmapi

nextcloud:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  middlewares:
    - https-redirect
  service: nextcloud

# Dev infrastructure (IP allowlist enforced)
hermes:
  rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
  middlewares:
    - https-redirect
    - ipAllowList
  service: hermes-webui

portainer:
  rule: "Host(`portainer.dev.aldof.duckdns.org`)"
  middlewares:
    - https-redirect
    - ipAllowList
  service: portainer
```

## Service URL Mapping

| Service Type | Network | URL Pattern |
|--------------|---------|-------------|
| Docker-networked | traefik_net | `http://container_name:port` |
| Host-networked | host | `http://<HOST_IP>:port` |
| Direct LAN + Traefik | traefik_net + host port | `http://<HOST_IP>:port` AND `http://container_name:port` |

**Example - Cockpit (host mode):**
```yaml
cockpit:
  loadBalancer:
    servers:
      - url: "http://192.168.0.28:9090"
```

**Example - Portainer (Docker network):**
```yaml
portainer:
  loadBalancer:
    servers:
      - url: "http://portainer:9000"
```

**Example - Plex (Docker network + direct LAN):**
```yaml
# In docker-compose.yml:
ports:
  - "32400:32400"

# In routes.yml (Traefik):
plex:
  loadBalancer:
    servers:
      - url: "http://plex:32400"
```

**Example - Hermes WebUI (Docker network, internal):**
```yaml
# In docker-compose.yml:
networks:
  - traefik_net

# In routes.yml (Traefik):
hermes-webui:
  loadBalancer:
    servers:
      - url: "http://hermes-webui:8787"
```

## Critical: Use Container Names for Docker-Networked Services

**Always use Docker container names (e.g., `http://hermes-webui:8787`) instead of hardcoded host IPs (e.g., `http://192.168.0.5:8787`) for services on the shared `traefik_net` network.**

### Why:
- Traefik runs on `traefik_net` and can resolve container names via Docker's internal DNS
- Hardcoded IPs break when the host IP changes (DHCP, static IP reconfiguration)
- Container name resolution is stable and doesn't require external routing

### Verification:
```bash
# Test from Traefik container
docker exec traefik wget -qO- http://hermes-webui:8787/health

# Test via Traefik HTTPS
curl -k -H "Host: web.hermes.dev.aldof.duckdns.org" https://localhost/health
```

## IP Allowlist Middleware

```yaml
middlewares:
  ipAllowList:
    ipAllowList:
      sourceRange:
        - "192.168.0.0/16"
        - "10.0.0.0/8"
        - "172.16.0.0/12"
        - "169.254.0.0/16"
        - "127.0.0.0/8"
        - "94.110.157.71/32"
```

Apply to dev.* routers:
```yaml
middlewares:
  - https-redirect
  - ipAllowList
```

## Verification Checklist

- [ ] Template: `templates/infra/04-network-traefik/routes.yml`
- [ ] Runtime: `/home/aldo/dev/04-network-traefik/routes.yml`
- [ ] Traefik restarted: `docker compose restart traefik`
- [ ] Test public: `curl -I https://freellm.aldof.duckdns.org` → 200
- [ ] Test dev: `curl -I https://portainer.dev.aldof.duckdns.org` → 307/200
- [ ] Old routes return 404: `curl -I https://portainer.aldof.duckdns.org` → 404
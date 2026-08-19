# Traefik IP-Based Access Control

## Overview
Use Traefik's `ClientIP()` matcher to restrict subdomain access to specific IP addresses or CIDR ranges. This is useful for internal-only services, admin dashboards, or secure remote access.

## Quick Reference

### Single IP Address
```yaml
my-service-http-91:
  rule: "Host(`my-service.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: my-service
my-service-https-91:
  rule: "Host(`my-service.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))"
  entryPoints:
    - websecure
  service: my-service
  tls:
    certResolver: myresolver
```

### CIDR Network Range
```yaml
my-service-internal:
  rule: "Host(`my-service.dev.aldof.duckdns.org`) && (ClientIP(`192.168.0.0/16`))"
  entryPoints:
    - websecure
  service: my-service
  tls:
    certResolver: myresolver
```

### Multiple IP Ranges (OR Logic)
```yaml
my-service-auth:
  rule: "(ClientIP(`192.168.0.0/16`)) || (ClientIP(`172.16.0.0/12`)) || (ClientIP(`10.0.0.0/8`))"
  entryPoints:
    - websecure
  service: my-service
  tls:
    certResolver: myresolver
```

### Combined Host and Path Restrictions
```yaml
admin-only:
  rule: "Host(`admin.dev.aldof.duckdns.org`) && (ClientIP(`192.168.1.0/24`)) && (PathPrefix(`/api`))"
  entryPoints:
    - websecure
  service: my-service
  tls:
    certResolver: myresolver
```

## Implementation Steps

1. **Plan IP Range**: Determine which IPs should have access
   - Single external office IP
   - Internal network ranges (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`)
   - VPN ranges

2. **Choose Method**: Two approaches available
   - **Method A: ClientIP() in router rule** (per-router, simple but repetitive)
   - **Method B: ipAllowList middleware** (centralized, recommended for multiple routers)

3. **Method B: ipAllowList Middleware (Recommended)**

   Define once in middlewares section:
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
           - "94.110.157.71/32"
   ```

   Apply to every router that needs it:
   ```yaml
   my-service-http:
     rule: "Host(`my-service.dev.aldof.duckdns.org`)"
     entryPoints:
       - web
     middlewares:
       - https-redirect
       - ipAllowList
     service: my-service
   my-service:
     rule: "Host(`my-service.dev.aldof.duckdns.org`)"
     entryPoints:
       - websecure
     service: my-service
     tls:
       certResolver: myresolver
     middlewares:
       - ipAllowList
   ```

4. **Deploy**: Run Ansible playbook
   ```bash
   cd /home/aldo/dev/01-core-infra && ./install.sh
   ```

5. **Verify**:
   ```bash
   # Check routes file
   docker exec traefik cat /etc/traefik/routes.yml | grep -A 8 "ipAllowList"
   
   # Test from allowed IP
   curl -I --interface 91.178.73.241 https://yoursubdomain.dev.aldof.duckdns.org
   
   # Test from denied IP (should fail with 404)
   curl -I --interface <denied-ip> https://yoursubdomain.dev.aldof.duckdns.org
   ```

## Common Pitfalls

### ❌ Wrong: Using IP in Host() only
```yaml
# WRONG - allows everyone to access via the hostname
rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
```

### ✅ Correct: IP in rule with ClientIP()
```yaml
# RIGHT - only specified IP can access
rule: "Host(`web.hermes.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))"
```

### ❌ Wrong: Unquoted Host value
```yaml
# WRONG - Traefik config invalid
rule: Host(web.hermes.dev.aldof.duckdns.org)
```

### ✅ Correct: Quoted Host value
```yaml
# RIGHT - valid Traefik syntax
rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
```

## Notes

- HTTP routers use `entryPoints: [web]` with `https-redirect` middleware
- HTTPS routers use `entryPoints: [websecure]` with `tls.certResolver`
- Always include both HTTP and HTTPS routers for proper redirect flow
- ClientIP matcher is case-sensitive and requires exact formatting
- For dynamic IPs, consider using a VPN or Tailscale access list instead

## Session 2026-08-08: Full Playbook Integration

### Hermes WebUI Deployment via Ansible

Added `02-ai-hermes-webui` to `container_services` in `ansible/roles/containers/defaults/main.yml`:

```yaml
container_services:
  # ... existing services ...
  # 02-ai-* -> in-repo runtime dirs (templates managed by 01-core-infra)
  - name: 02-ai-hermes-webui
    runtime_dir: "/home/aldo/dev/01-core-infra/02-ai-hermes-webui"
```

Created template at `templates/infra/02-ai-hermes-webui/docker-compose.yml`:
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

### IP Allowlist Applied to All Subdomains

The `ipAllowList` middleware is now applied to **all** dev-subdomain routers:
- `freellm.aldof.duckdns.org`
- `cloud.aldof.duckdns.org`
- `web.hermes.dev.aldof.duckdns.org`
- `aldof.duckdns.org` (homepage)
- `vault.aldof.duckdns.org`
- `taskqueue.aldof.duckdns.org`
- `portainer.aldof.duckdns.org` (NEW)
- `cockpit.aldof.duckdns.org` (NEW)
- `plex.aldof.duckdns.org` (NEW)
- `qbittorrent.aldof.duckdns.org` (NEW)
- `torrent.aldof.duckdns.org` (NEW - alias for qbittorrent)

This ensures only internal IPs (192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 169.254.0.0/16, 127.0.0.0/8, 94.110.157.71/32) can access any dev subdomain.

### Cockpit on Host Network

Cockpit runs with `network_mode: host` so it's not on the `traefik_net` Docker network. The Traefik service URL must point to the host's actual IP:

```yaml
cockpit:
  loadBalancer:
    servers:
      - url: "http://192.168.0.28:9090"  # Host IP, not container name
```

The compose template for cockpit at `templates/infra/01-core-cockpit/docker-compose.yml`:
```yaml
services:
  cockpit:
    image: quay.io/cockpit/ws:latest
    container_name: cockpit
    restart: unless-stopped
    network_mode: host
    volumes:
      - /run:/run
    ports:
      - "9090:9090"
```

### Verification

```bash
# Check middleware in runtime routes
docker exec traefik cat /etc/traefik/routes.yml | grep -A 8 "ipAllowList:"

# Test from internal IP (should succeed)
curl -I -k https://web.hermes.dev.aldof.duckdns.org --resolve web.hermes.dev.aldof.duckdns.org:443:192.168.0.5

# Test from external IP (should 404)
curl -I --interface 91.178.73.241 https://web.hermes.dev.aldof.duckdns.org

# Verify all new subdomains
curl -sk -I https://portainer.aldof.duckdns.org
curl -sk -I https://cockpit.aldof.duckdns.org
curl -sk -I https://plex.aldof.duckdns.org
curl -sk -I https://qbittorrent.aldof.duckdns.org
curl -sk -I https://torrent.aldof.duckdns.org
```

## Session 2026-08-08: Nextcloud Recovery

### Missing .ncdata File Fix

When Nextcloud reports "Your data directory is invalid. Ensure there is a file called '.ncdata'", create it:

```bash
echo "# Nextcloud data directory" > /mnt/HDD1/nextcloud/data/.ncdata
chown www-data:www-data /mnt/HDD1/nextcloud/data/.ncdata
```

### Database Network Isolation Fix

When Nextcloud app and DB are on different Docker networks (e.g., app on `traefik_net`, DB on `nextcloud_default`), they can't communicate. Fix by putting both on `traefik_net`:

```yaml
services:
  db:
    # ...
    networks:
      - traefik_net
  app:
    # ...
    networks:
      - traefik_net
networks:
  traefik_net:
    external: true
```

### MariaDB User Initialization

If MariaDB doesn't create users (because volume has pre-existing data), remove and recreate the volume:

```bash
docker compose -f /home/aldo/dev/01-core-infra/nextcloud/docker-compose.yml down -v
MYSQL_ROOT_PASSWORD=changeme_root MYSQL_PASSWORD=changeme_user docker compose -f /home/aldo/dev/01-core-infra/nextcloud/docker-compose.yml up -d
```

### Nextcloud Installation & Configuration

```bash
# Install Nextcloud
docker exec nextcloud-app-1 php occ maintenance:install \
  --database=mysql \
  --database-name=nextcloud \
  --database-user=nextcloud \
  --database-pass="changeme_user" \
  --database-host=db \
  --admin-user=aldo \
  --admin-pass="changeme_admin"

# Configure trusted domains and proxy headers
docker exec -u www-data nextcloud-app-1 php occ config:system:set trusted_domains 1 --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwritehost --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwriteprotocol --value=https
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwritecondaddr --value='\.aldof\.duckdns\.org$'
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwrite.cli.url --value=https://cloud.aldof.duckdns.org
docker exec -u www-data nextcloud-app-1 php occ config:system:set trusted_proxies 0 --value=172.18.0.0/16
```
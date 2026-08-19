# Media Services Deployment (05-media-*) - Fix Summary

## Problem Identified (2026-08-04)

The `container_services` list in `ansible/roles/containers/defaults/main.yml` included 05-media-plex, 05-media-qbittorrent, and 05-media-nextcloud, but their runtime directories didn't exist and the compose templates had issues:

| Service | Template Issue | Missing Runtime Dir |
|---------|---------------|---------------------|
| plex | `network_mode: host` (incompatible with traefik_net), relative paths `./config`, `~/media/movies` | `/home/aldo/dev/01-core-infra/plex/` |
| qbittorrent | No network config, no restart policy, relative paths `./config`, `./downloads` | `/home/aldo/dev/01-core-infra/qbittorrent/` |
| nextcloud | Used `${MYSQL_ROOT_PASSWORD}` env vars without .env template, hardcoded `/mnt/HDD1/nextcloud` | `/home/aldo/dev/01-core-infra/nextcloud/` |

## Fixes Applied

### 1. Plex Template (`templates/infra/05-media-plex/docker-compose.yml`)
- **Removed** `network_mode: host` (incompatible with Traefik bridge network)
- **Added** `traefik_net` network
- **Replaced** relative paths with absolute HDD paths:
  - `/mnt/HDD1/plex/config:/config`
  - `/mnt/HDD1/media/movies:/movies`
  - `/mnt/HDD1/media/tv:/tv`
- **Added** `restart: unless-stopped`

### 2. Qbittorrent Template (`templates/infra/05-media-qbittorrent/docker-compose.yml`)
- **Added** `traefik_net` network
- **Added** `restart: unless-stopped`
- **Replaced** relative paths with absolute HDD paths:
  - `/mnt/HDD1/qbittorrent/config:/config`
  - `/mnt/HDD1/downloads:/downloads`

### 3. Nextcloud Template (`templates/infra/05-media-nextcloud/docker-compose.yml`)
- **Removed** obsolete `version: '3.9'` field (Docker Compose v2 ignores it)
- **Replaced** hardcoded env vars with placeholders:
  - `${MYSQL_ROOT_PASSWORD}`
  - `${MYSQL_PASSWORD}`
- **Kept** absolute path `/mnt/HDD1/nextcloud:/var/www/html`

### 4. Traefik Routes (`templates/infra/04-network-traefik/routes.yml`)
Added HTTP router entries for:
- `plex.aldof.duckdns.org` → `plex:32400`
- `qbittorrent.aldof.duckdns.org` → `qbittorrent:8080`

Each with:
- HTTPS redirect middleware
- TLS certResolver: myresolver
- ipAllowList middleware for IP restriction

### 5. Vault Credentials (`vaults/nextcloud-credentials.yml`)
Created placeholder vault file:
```yaml
vault_nextcloud_mysql_root_password: "changeme_root"
vault_nextcloud_mysql_password: "changeme_user"
```

### 6. Containers Role (`ansible/roles/containers/tasks/main.yml`)
Added `include_vars` task to load nextcloud vault credentials before deployment.

## Fixes Applied (2026-08-08)

### Nextcloud Data Directory & Network Fixes (Session 2026-08-08)

During the full playbook test, two additional issues were discovered and fixed:

#### 1. Missing `.ncdata` File
**Error**: `Your data directory is invalid. Ensure there is a file called ".ncdata" in the root of the data directory.`
**Fix**: Created the marker file in the data directory:
```bash
echo "# Nextcloud data directory" > /mnt/HDD1/nextcloud/data/.ncdata
chown www-data:www-data /mnt/HDD1/nextcloud/data/.ncdata
```
Note: This file must exist for Nextcloud to validate the data directory on startup.

#### 2. Database Network Isolation
**Error**: `SQLSTATE[HY000] [2002] php_network_getaddresses: getaddrinfo for db failed`
**Root Cause**: The Nextcloud app was on `traefik_net` but the database was on `nextcloud_default` network (separate Docker Compose project). They couldn't resolve each other's hostnames.
**Fix**: Updated `templates/infra/05-media-nextcloud/docker-compose.yml` to put **both** db and app services on `traefik_net`:
```yaml
services:
  db:
    # ... existing config ...
    networks:
      - traefik_net
  app:
    # ... existing config ...
    networks:
      - traefik_net
```
Then removed the stale database volume and recreated containers:
```bash
docker compose -f /home/aldo/dev/01-core-infra/nextcloud/docker-compose.yml down -v
MYSQL_ROOT_PASSWORD=changeme_root MYSQL_PASSWORD=changeme_user docker compose -f /home/aldo/dev/01-core-infra/nextcloud/docker-compose.yml up -d
```

#### 3. MariaDB User Initialization
The mariadb entrypoint creates users/databases only on **first run** (empty volume). Since the volume had pre-existing data from previous failed attempts, users weren't created.
**Fix**: Remove and recreate the database volume (`docker compose down -v`) to trigger fresh initialization with environment variables.

### Updated Template (`templates/infra/05-media-nextcloud/docker-compose.yml`)
```yaml
services:
  db:
    image: mariadb:10.6
    restart: always
    volumes:
      - db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    networks:
      - traefik_net

  app:
    image: nextcloud:34-apache
    restart: always
    volumes:
      - /mnt/HDD1/nextcloud:/var/www/html
    environment:
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    networks:
      - traefik_net
    depends_on:
      - db
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

volumes:
  db_data:

networks:
  traefik_net:
    external: true
```

### Post-Install Configuration (Required)
After deployment, run these commands to configure Nextcloud for Traefik proxy:
```bash
docker exec -u www-data nextcloud-app-1 php occ config:system:set trusted_domains 1 --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwritehost --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwriteprotocol --value=https
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwritecondaddr --value='\.aldof\.duckdns\.org$'
docker exec -u www-data nextcloud-app-1 php occ config:system:set overwrite.cli.url --value=https://cloud.aldof.duckdns.org
docker exec -u www-data nextcloud-app-1 php occ config:system:set trusted_proxies 0 --value=172.18.0.0/16
```

### Separate Nextcloud Instance
A separate Nextcloud instance exists at `/home/aldo/dev/06-apps-nextcloud/` (managed outside 01-core-infra) with its own docker-compose.yml. The 05-media-nextcloud template deploys a *second* instance. Coordinate to avoid port/volume conflicts.

### User Preference
User prefers routes.yml for Traefik configuration (not Docker labels on containers). All Traefik routing is managed centrally via the routes.yml template.

### Plex Direct LAN Access (2026-08-11)
**Problem**: Plex was accessible via Traefik at `https://plex.aldof.duckdns.org/` but not directly at `http://192.168.0.5:32400/` (connection refused).

**Root Cause**: The Plex docker-compose template only attached the container to `traefik_net` network but did not publish port 32400 to the host. Traefik routes worked because they use Docker's internal DNS resolution on the shared bridge network, but direct LAN access requires host port binding.

**Fix**: Added port mapping to `templates/infra/05-media-plex/docker-compose.yml`:
```yaml
ports:
  - "32400:32400"
```

**Verification**:
```bash
# Direct LAN access
curl -s -o /dev/null -w "%{http_code}" http://192.168.0.5:32400/  # Returns 401 (unauthenticated)

# Via Traefik (still works)
curl -sk -o /dev/null -w "%{http_code}" -H "Host: plex.aldof.duckdns.org" https://localhost:443/  # Returns 401
```

**Note**: The 401 response confirms Plex is running and accepting connections (unauthenticated access is expected without a claim token).
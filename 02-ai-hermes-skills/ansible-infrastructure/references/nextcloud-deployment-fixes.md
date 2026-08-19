# Nextcloud Deployment Fixes

## Issue 1: Missing .ncdata File

**Error:** "Your data directory is invalid. Ensure there is a file called '.ncdata' in the root of the data directory."

**Fix:**
```bash
echo "# Nextcloud data directory" > /mnt/HDD1/nextcloud/data/.ncdata
chown www-data:www-data /mnt/HDD1/nextcloud/data/.ncdata
```

**Note:** If filesystem doesn't support chown (e.g., NTFS/FAT32), file creation with correct ownership via container may be needed.

## Issue 2: Database Network Isolation

**Problem:** Nextcloud app on `traefik_net`, MariaDB on `nextcloud_default` network - cannot communicate.

**Root Cause:** Compose template only added `traefik_net` to app service, not db service.

**Fix in docker-compose.yml:**
```yaml
services:
  db:
    # ... config ...
    networks:
      - traefik_net  # ADD THIS
  
  app:
    # ... config ...
    networks:
      - traefik_net

networks:
  traefik_net:
    external: true
```

## Issue 3: Stale Database Volume

**Problem:** MariaDB entrypoint doesn't create users/databases if volume already has data from previous failed init.

**Fix:**
```bash
# Stop and remove with volumes
docker compose -f nextcloud/docker-compose.yml down -v

# Recreate with fresh volume
MYSQL_ROOT_PASSWORD=xxx MYSQL_PASSWORD=yyy docker compose -f nextcloud/docker-compose.yml up -d
```

## Issue 4: Nextcloud Behind Traefik Proxy Headers

**Required occ commands after install:**
```bash
docker exec -u www-data nextcloud php occ config:system:set trusted_domains 1 --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set overwritehost --value=cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set overwriteprotocol --value=https
docker exec -u www-data nextcloud php occ config:system:set overwritecondaddr --value='\.aldof\.duckdns\.org$'
docker exec -u www-data nextcloud php occ config:system:set overwrite.cli.url --value=https://cloud.aldof.duckdns.org
docker exec -u www-data nextcloud php occ config:system:set trusted_proxies 0 --value=172.18.0.0/16
```

## Verification
```bash
curl -I https://cloud.aldof.duckdns.org/
# Should return 302 to https://cloud.aldof.duckdns.org/login (NOT http://nextcloud/login)
```

## 2026-08-08 Session: Complete Recovery

This session demonstrated a full Nextcloud recovery from broken state:

1. **Missing .ncdata** → Created marker file
2. **Network isolation** → Updated compose to put DB and app on same `traefik_net`
3. **Stale DB volume** → Used `docker compose down -v` to reset
4. **Fresh install** → `occ maintenance:install` with correct credentials
5. **Proxy config** → Applied all 6 occ commands for Traefik compatibility

**Working template** at `templates/infra/05-media-nextcloud/docker-compose.yml` with both services on `traefik_net`.
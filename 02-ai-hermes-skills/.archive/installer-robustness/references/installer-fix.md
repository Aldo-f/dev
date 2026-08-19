# Installer Robustness - Real Installation Example

## Complete Workflow: 18TB HDD + Nextcloud with DuckDNS

### 1. Disk Detection and Verification

**Problem**: Need to reliably identify and mount large storage devices for container persistence.

**Solution**:
```bash
# Detect storage devices with filesystem info
lsblk -f

# Find persistent device identifiers
ls -l /dev/disk/by-id/

# Expected output includes:
# /dev/disk/by-id/ata-WD_Elements_25A3_335A47503547595A-0:0 -> ../../sda
# /dev/disk/by-id/wwn-0x5000cca2e9c9a05f -> ../../sda

# Check if device has partitions
fdisk -l | grep /dev/sda
```

**Expected Results**:
```
Disk /dev/sda: 17.1 TiB, 18006311652416 bytes
Disklabel type: gpt
Disk identifier: D1955C62-9C8F-44B2-BF68-33CC7023C346

Device     Start         End     Sectors  Size Type
/dev/sda1   2048 35156588543 35156586496 16.4T Linux filesystem
```

### 2. Storage Mounting

**Problem**: Mount the device and make it persistent across reboots.

**Solution**:
```bash
# Create mount point with proper ownership
sudo mkdir -p /mnt/HDD1

# Mount filesystem with rw options for Docker containers
sudo mount /dev/sda1 /mnt/HDD1

# Verify mounting
mount | grep /mnt/HDD1
df -h /mnt/HDD1

# Expected output:
# /dev/sda1 on /mnt/HDD1 type ext4 (rw,relatime)
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1       17T  1.8T   14T  12% /mnt/HDD1

# Make persistent mount
sudo echo '/dev/sda1 /mnt/HDD1 ext4 defaults,noatime 0 0' >> /etc/fstab
```

### 3. Container Directory Structure

**Problem**: Isolate application code from persistent data.

**Solution**:
```bash
# Create container app structure
mkdir -p /home/aldo/dev/06-apps-nextcloud/nextcloud
mkdir -p /home/aldo/dev/06-apps-nextcloud/db

# Set proper ownership for container access
sudo chown -R 33:33 /mnt/HDD1/nextcloud/data  # www-data:www-data

# Create Nextcloud application directory
mkdir -p /home/aldo/dev/06-apps-nextcloud/nextcloud
mkdir -p /home/aldo/dev/06-apps-nextcloud/db
```

### 4. Docker Compose Configuration

**Problem**: Deploy container apps that persist data to external storage.

**Solution**:

**docker-compose.yml**:
```yaml
version: "3.9"

services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    restart: unless-stopped
    ports:
      - "8888:80"
    volumes:
      - ./nextcloud:/var/www/html:rw
      - /mnt/HDD1/nextcloud/data:/var/www/html/data:rw
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloudpassword
      - MYSQL_ROOT_PASSWORD=rootpassword
    networks:
      - traefik_net

  db:
    image: mariadb:latest
    container_name: nextcloud-db
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloudpassword
    volumes:
      - ./db:/var/lib/mysql
    networks:
      - traefik_net

networks:
  traefik_net:
    external: true
```

### 5. DuckDNS Integration

**Problem**: Route external domains to local container services.

**Solution**:

**traefik/routes.yml**:
```yaml
http:
  routers:
    nextcloud:
      rule: "Host(`cloud.aldof.duckdns.org`)"
      entryPoints:
        - websecure
      service: nextcloud
      tls:
        certResolver: myresolver

    nextcloud-http:
      rule: "Host(`cloud.aldof.duckdns.org`)"
      entryPoints:
        - web
      middlewares:
        - https-redirect
      service: nextcloud

  services:
    nextcloud:
      loadBalancer:
        servers:
          - url: "http://nextcloud:80"

  middlewares:
    https-redirect:
      redirectScheme:
        scheme: https
        permanent: true
```

**traefik.yml**:
```yaml
entrypoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  file:
    filename: /etc/traefik/routes.yml

certificatesResolvers:
  myresolver:
    acme:
      email: "aldof@duckdns.org"
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web
```

### 6. Deployment Commands

**Problem**: Deploy containers from scripts where SCRIPT_DIR may not be reliable.

**Solution**:
```bash
# Deploy using absolute paths (works from piped scripts)
docker-compose -f /home/aldo/dev/06-apps-nextcloud/docker-compose.yml up -d

# Verify deployment
docker ps | grep nextcloud

# Expected output:
# cc7c4cc6917b   mariadb:latest                            "docker-entrypoint.s…"   44 minutes ago   Up 44 minutes          10 seconds ago   Up 44 minutes          3306/tcp                                    nextcloud-db
c863c83077d9   nextcloud:latest                          "/entrypoint.sh apac…"   44 minutes ago   Up 44 minutes          0.0.0.0:8888->80/tcp, :::8888->80/tcp       nextcloud
```

### 7. Verification and Troubleshooting

**Problem**: Debug container deployment and external access issues.

**Solution**:

**Check container status**:
```bash
# Verify Nextcloud is running
docker ps | grep nextcloud

# Check Nextcloud logs
docker logs nextcloud

# Check database connectivity
docker exec nextcloud-db mysql -u nextcloud -pnextcloudpassword -h localhost
```

**Test external access**:
```bash
# Test local access
curl -I http://localhost:8888

# Test Docker network access
docker exec nextcloud curl -I http://nextcloud

# Verify DNS propagation (after DuckDNS configuration)
curl -I https://cloud.aldof.duckdns.org/
```

**Common failure patterns**:
```bash
# ERROR: use of closed network connection
# Fix: Ensure required networks exist before deployment
# docker network ls
# docker network create traefik_net --driver bridge

# Permission denied on mount
# Fix: Use :rw mount options for container write access
# Update: ./nextcloud:/var/www/html:rw

# Container name conflicts
# Fix: Remove existing containers before deployment
# docker rm -f nextcloud nextcloud-db
```

### 8. Post-Deployment Verification

**Check application functionality**:
```bash
# Access via local port
hostname -I | xargs -I {} curl -L http://{}:8888

# Verify data persistence
ls -la /mnt/HDD1/nextcloud/data/
ls -la /home/aldo/dev/06-apps-nextcloud/nextcloud/

# Check disk usage
df -h /mnt/HDD1
lsblk -f /dev/sda1
```

## Key Success Indicators

- **Storage**: `/dev/sda1` mounted as `/mnt/HDD1` with ext4
- **Permissions**: Proper ownership for container access
- **Network**: Both container and external DuckDNS access
- **Persistence**: Data survives container restarts
- **Accessibility**: HTTPS via DuckDNS domain
# Nextcloud Deployment with Persistent Storage

## Pattern Summary
Nextcloud deployment that uses persistent storage via HDD mount for data while keeping application code separate. This pattern ensures data survives container rebuilds and maintains proper separation of concerns.

## Key Configuration
- **Persistent Storage Path**: `/mnt/HDD1/nextcloud/data` (mounted HDD)
- **Application Code**: `./nextcloud/` (container-local, rebuilt on updates)
- **Database**: `./db:/var/lib/mysql` (container-local persistence)
- **Network**: Connected to external `traefik_net`
- **Ports**: `8888:80` (host:Container)

## Docker Compose Structure
```yaml
services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    volumes:
      - ./nextcloud:/var/www/html:rw     # Application code
      - /mnt/HDD1/nextcloud/data:/var/www/html/data:rw  # Persistent data
    
  db:
    image: mariadb:latest
    container_name: nextcloud-db
    volumes:
      - ./db:/var/lib/mysql  # Database persistence
    
networks:
  traefik_net:
    external: true  # Pre-existing network
```

## Directory Layout
```
06-apps-nextcloud/
├── docker-compose.yml          # Container configuration
├── nextcloud/                  # Nextcloud app code (rebuild-friendly)
│   ├── 3rdparty/
│   ├── apps/
│   └── ... (Nextcloud files)
├── db/                        # Database persistence (rebuild-friendly)
└── .gitignore               # Exclude temp files
```

## Storage Management Steps
1. **Verify HDD Mount**: `df -h /mnt/HDD1` and `lsblk -f /dev/sda1`
2. **Create Directory Structure**: 
   - `mkdir -p /home/aldo/dev/06-apps-nextcloud/nextcloud`
   - `mkdir -p /home/aldo/dev/06-apps-nextcloud/db`
3. **Mount Persistent Data**:
   ```bash
   sudo mkdir -p /mnt/HDD1/nextcloud/data
   sudo mount /dev/sda1 /mnt/HDD1
   sudo chown -R 33:33 /mnt/HDD1/nextcloud/data  # www-data:www-data
   ```
4. **Deploy**: `docker-compose -f /path/to/docker-compose.yml up -d`

## Benefits
- **Data Persists**: Nextcloud user files survive container rebuilds
- **Clean Separation**: App code vs user data management
- **Easy Upgrades**: Application code can be updated without affecting user data
- **Backup-Friendly**: Separate file systems for point-in-time recovery
- **Permission Control**: Fine-grained control over data directory access

## Common Issues
- **Permission Denied**: Ensure `www-data` user has write access to data directory
- **Docker Network**: Must exist before deployment (`traefik_net` in this pattern)
- **Volume Mounts**: Use `:rw` for read-write access when needed
- **Rebuild Impacts**: Application directory gets overwritten on next deploy
# Media File Organization

## Pattern: Shared Media Libraries (Plex + qBittorrent + Nextcloud)

When organizing media files for multiple services, use symlinks to maintain a single source of truth while providing service-specific access paths.

### Directory Structure

```
/mnt/HDD1/
├── media/                     # Plex access point
│   ├── movies → aldo/files/media/movies
│   ├── tv → aldo/files/media/tv
│   └── music → aldo/files/media/music
├── seed/                      # qBittorrent seed access
│   └── → aldo/files/seed
└── nextcloud/data/aldo/files/
    ├── media/                 # Primary storage
    │   ├── movies/            # 13 folders, 1230 files
    │   ├── tv/                # 37 folders
    │   └── music/
    │       └── _seed → ../../seed/media/music
    ├── seed/                  # Seeder storage
    │   ├── media/
    │   │   ├── movies/
    │   │   ├── tv/
    │   │   └── music/
    │   └── apps/
    └── [other user folders]
```

### Implementation Steps

**1. Create directories:**
```bash
cd /mnt/HDD1/nextcloud/data/aldo/files
mkdir -p media/{movies,tv,music}
mkdir -p seed/media/{movies,tv,music} seed/apps
```

**2. Move existing content:**
```bash
# Move from old location to new structure
sudo mv Documents/Torrents/media/movies/* media/movies/
sudo mv Documents/Torrents/media/tv/* media/tv/
sudo mv Documents/Torrents/media/music/* media/music/
sudo mv Documents/Torrents/seed/* seed/media/movies/
```

**3. Create _seed symlinks (for seeding from media folders):**
```bash
cd media
ln -s ../../seed/media/movies movies/_seed
ln -s ../../seed/media/tv tv/_seed
ln -s ../../seed/media/music music/_seed
```

**4. Create external symlinks (for Plex/qBittorrent):**
```bash
sudo mkdir -p /mnt/HDD1/media
sudo ln -s /mnt/HDD1/nextcloud/data/aldo/files/media/movies /mnt/HDD1/media/movies
sudo ln -s /mnt/HDD1/nextcloud/data/aldo/files/media/tv /mnt/HDD1/media/tv
sudo ln -s /mnt/HDD1/nextcloud/data/aldo/files/media/music /mnt/HDD1/media/music
sudo ln -s /mnt/HDD1/nextcloud/data/aldo/files/seed /mnt/HDD1/seed
```

**5. Configure services:**

**Plex:**
- Movies library: `/mnt/HDD1/media/movies`
- TV library: `/mnt/HDD1/media/tv`

**qBittorrent:**
- Download directory: `/mnt/HDD1/downloads` (symlink to seed)
- Categories map to subfolders:
  - `tv` → `/mnt/HDD1/media/tv`
  - `movies` → `/mnt/HDD1/media/movies`
  - `music` → `/mnt/HDD1/media/music`

### qBittorrent Container Setup

```bash
# Remove old container
docker stop qbittorrent && docker rm qbittorrent

# Recreate with proper mounts
docker run -d --name qbittorrent \
  -e PUID=1000 -e PGID=1000 -e TZ=Europe/Brussels \
  -p 8091:8080 \
  -v /mnt/HDD1/qbittorrent/config:/config \
  -v /mnt/HDD1/nextcloud/data/aldo/files/seed:/downloads/seed:shared \
  lscr.io/linuxserver/qbittorrent:latest
```

### Verification

```bash
# Check Plex access
docker exec plex ls /movies/ | wc -l
docker exec plex ls /tv/ | wc -l

# Check qBittorrent access
docker exec qbittorrent ls /downloads/seed/media/

# Check Nextcloud
curl -sk -I https://cloud.aldof.duckdns.org/login | head -1
```

## Common Pitfalls

1. **qBittorrent can't see symlinks**: Use `shared` propagation mode for Docker mounts:
   ```bash
   -v /path/to/seed:/downloads/seed:shared
   ```

2. **Permission denied**: Ensure www-data group has access:
   ```bash
   sudo chown -R aldo:www-data /mnt/HDD1/nextcloud/data/aldo/files
   ```

3. **Empty directories after move**: Run Nextcloud file scan:
   ```bash
   docker exec nextcloud php occ files:scan --all
   ```

4. **Stale _seed symlinks**: Remove duplicate symlinks that point to themselves:
   ```bash
   rm media/tv/tv media/movies/movies media/music/music
   ```

5. **Docker container name conflicts**: Always stop and remove old container before recreating:
   ```bash
   docker rm -f qbittorrent  # Force remove if needed
   ```

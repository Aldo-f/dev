# Media Stack Migration: SSD Compose + HDD Data Pattern

**Context:** Session where Plex, qBittorrent, and Nextcloud compose templates were migrated from `templates/infra/05-media-*` to runtime directories `~/dev/05-media-*` on SSD, while all data remains on `/mnt/HDD1/nextcloud/data/aldo/`.

**Trigger:** User required moving docker-compose.yml files to proper 05-media locations per group taxonomy, with shared HDD data directory for interoperability.

## Architecture Pattern

```
~/dev/05-media-plex/docker-compose.yml       ← SSD (compose template deployed here)
~/dev/05-media-qbittorrent/docker-compose.yml
~/dev/05-media-nextcloud/docker-compose.yml

/mnt/HDD1/nextcloud/data/aldo/               ← HDD (single source of truth)
├── config/          # Nextcloud config.php
└── files/           # SHARED MEDIA DATA (PRESERVED)
    ├── movie1.mp4
    ├── movie2.mkv
    └── series1.mp4

/mnt/HDD1/plex/config/                       # Plex config only
/mnt/HDD1/qbittorrent/config/                # qBittorrent config only
```

## Service Volume Mounts (All PUID=1000, PGID=1000)

| Service | Host Path | Container Path | Mode | Purpose |
|---------|-----------|----------------|------|---------|
| **plex** | `/mnt/HDD1/plex/config` | `/config` | rw | Plex config |
| **plex** | `/mnt/HDD1/nextcloud/data/aldo/files` | `/media` | **ro** | Media playback |
| **qbittorrent** | `/mnt/HDD1/qbittorrent/config` | `/config` | rw | qBittorrent config |
| **qbittorrent** | `/mnt/HDD1/nextcloud/data/aldo/files` | `/downloads` | **rw** | Torrent downloads |
| **nextcloud** | `/mnt/HDD1/nextcloud/data/aldo` | `/var/www/html/data` | **rw** | File management |

## Key Design Decisions

1. **Single shared data directory** — All three services use `/mnt/HDD1/nextcloud/data/aldo/files/` as the canonical media location. No duplication, no sync needed.

2. **Read-only for Plex** — Plex mounts `:ro` to prevent accidental modifications during playback/indexing.

3. **Read-write for qBittorrent & Nextcloud** — qBittorrent downloads directly to the shared location; Nextcloud provides file management UI.

4. **Unified UID/GID (1000)** — All containers run as `aldo` (UID 1000). Host path ownership must match: `sudo chown -R 1000:1000 /mnt/HDD1/nextcloud/data/aldo`.

5. **Traefik labels on containers** — Each compose includes Traefik labels for automatic route discovery (supplements routes.yml).

6. **Ansible runtime dirs updated** — `ansible/roles/containers/defaults/main.yml` now points to `~/dev/05-media-*`.

## Critical Safety Constraint

> **DO NOT, UNDER ANY CIRCUMSTANCES, LOSE DATA FROM /mnt/HDD1/nextcloud/data/aldo/files/**

This is a P0 (blocker) requirement. Migration must be zero-data-loss.

## Verification Protocol

```bash
# Pre-migration baseline
find /mnt/HDD1/nextcloud/data/aldo/files -type f -exec sha256sum {} + | sort > /tmp/pre.sha256

# Post-deployment verification
find /mnt/HDD1/nextcloud/data/aldo/files -type f -exec sha256sum {} + | sort > /tmp/post.sha256
diff -u /tmp/pre.sha256 /tmp/post.sha256 && echo "✅ Zero data loss"

# Container health
docker ps --filter "name=plex" --filter "name=qbittorrent" --filter "name=nextcloud" --filter "name=nextcloud-db"

# Volume mount verification
docker inspect plex | grep -A5 Mounts
docker inspect qbittorrent | grep -A5 Mounts
docker inspect nextcloud | grep -A5 Mounts

# Functional tests
# Plex: https://plex.aldof.duckdns.org → library /media → play test file
# qBittorrent: https://qbittorrent.aldof.duckdns.org → add torrent → verify download
# Nextcloud: https://cloud.aldof.duckdns.org → Files app → CRUD test
```

## Permission Fix (Required Before Deploy)

```bash
# Existing Nextcloud runs as www-data (UID 33), new stack runs as aldo (UID 1000)
sudo chown -R 1000:1000 /mnt/HDD1/nextcloud/data/aldo
# Verify
ls -ld /mnt/HDD1/nextcloud/data/aldo/files
# drwxr-xr-x 2 aldo aldo 4096 ... files
```

## Ansible Changes Made

**File:** `ansible/roles/containers/defaults/main.yml`

```yaml
container_services:
  # ... existing entries ...
  # 05-media-* -> sibling dev repo dirs
  - name: 05-media-plex
    runtime_dir: "/home/aldo/dev/05-media-plex"
  - name: 05-media-qbittorrent
    runtime_dir: "/home/aldo/dev/05-media-qbittorrent"
  - name: 05-media-nextcloud
    runtime_dir: "/home/aldo/dev/05-media-nextcloud"
```

**Files:** `templates/infra/05-media-*/docker-compose.yml` — All updated with shared data mounts, Traefik labels, PUID/PGID=1000.

## Rollback Procedure

```bash
# 1. Stop new stack
cd ~/dev/05-media-plex && docker compose down
cd ~/dev/05-media-qbittorrent && docker compose down
cd ~/dev/05-media-nextcloud && docker compose down

# 2. Revert Ansible runtime_dirs to old paths (01-core-infra subdirs)
# 3. Re-run playbook
# 4. Original 06-apps-nextcloud at ~/dev/06-apps-nextcloud/ remains untouched
```

## Spec-Kit Integration

This migration used GitHub Spec-Kit for specification-driven development:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init --here --integration generic --integration-options="--commands-dir .specify/commands"
# Created: SPEC.md, PLAN.md, tasks.md, quickstart.md
```

## Traefik Route Integration

Routes already existed in `templates/infra/04-network-traefik/routes.yml`:
- `plex.aldof.duckdns.org` → plex:32400
- `qbittorrent.aldof.duckdns.org` → qbittorrent:8080
- `cloud.aldof.duckdns.org` → nextcloud:80

Container labels provide redundant route definition for resilience.

## Lessons Learned

1. **Shared data directory requires permission alignment** — Container UID must match host directory owner, or files become inaccessible.

2. **Spec-Kit adds rigor** — SPEC.md/PLAN.md/tasks.md structure forced clear requirements, edge cases, and verification steps before implementation.

3. **Ansible container_services is the single source of truth** — Runtime directories, compose deployment, and Traefik sync all driven from this list.

4. **Docker Compose v2 only** — Use `docker compose` (plugin), never `docker-compose`.

5. **Idempotency verified** — Second playbook run shows `changed=0` for container tasks.

6. **Rollback plan documented** — Original 06-apps-nextcloud instance preserved as safety net.
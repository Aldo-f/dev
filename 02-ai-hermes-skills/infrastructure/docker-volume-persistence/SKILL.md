---
name: docker-volume-persistence
description: "Mount disks and manage Docker persistent volume ownership."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Docker, Persistence, HDD, Troubleshooting, Permissions]
    related_skills: [ansible-troubleshooting, git-workflow-troubleshooting]
---

# Docker Volume Persistence

This skill covers the standard pattern for persistent storage in Docker, specifically when mapping volumes to mounted host directories (e.g., external HDDs).

## 1. Disk Preparation & Mounting

When using external storage (HDD/SSD):
1.  **Identify:** `lsblk -o NAME,SIZE,TYPE,MOUNTPOINT`
2.  **Mount:** Create a mount point and mount the partition:
    ```bash
    sudo mkdir -p /mnt/HDD1
    sudo mount /dev/sda1 /mnt/HDD1
    ```
3.  **Persistent Mount:** Add to `/etc/fstab` (use UUID for reliability).

## 2. Docker Volume Persistence Pattern

Map host directories to container paths in your `docker-compose.yml`:

```yaml
services:
  app:
    volumes:
      - /mnt/HDD1/app/data:/var/www/html/data:rw
```

## 3. The Ownership Pitfall

The most common cause for container crashes (especially with web applications like Nextcloud) is **UID/GID mismatch**. 
- Containers often run as a specific user (e.g., `www-data`, UID 33).
- If the host-mounted directory is owned by `root` or a different user, the container will likely crash with a **Segmentation fault (11)**.

### Fix
Always correct ownership for the mapped host directory:
```bash
# Example for Nextcloud/www-data (UID 33)
sudo chown -R 33:33 /mnt/HDD1/app/data
```

### Debugging Pattern
If a container constantly restarts or crashes on startup:
1.  Check logs: `docker logs <container-name> --tail 50`
2.  Look for `Segmentation fault` or permission denied errors.
3.  Verify ownership: `ls -la /host/path/to/data`
4.  Correct ownership if mismatch found.

# Pi 5 HDD Mount Verification

## Current State (2026-08-08)
- `/dev/sdb1` (16.4TB ext4) is present but NOT mounted
- `/etc/fstab` has commented-out entry pointing to wrong device (`/dev/sda1`)
- Data directory `/mnt/HDD1/` exists but shows root filesystem usage

## Fix Required

### 1. Fix fstab Entry
```bash
# Remove old commented line
sudo sed -i '/#.*HDD1/d' /etc/fstab

# Add correct entry (sdb1, not sda1)
echo '/dev/sdb1 /mnt/HDD1 ext4 defaults,noatime 0 2' | sudo tee -a /etc/fstab
```

### 2. Mount the Drive
```bash
sudo mount -a
df -hT /mnt/HDD1
```

### 3. Set Permissions
```bash
# Data should be owned by www-data for Nextcloud/Plex/etc
sudo chown -R aldo:www-data /mnt/HDD1
sudo chmod -R 750 /mnt/HDD1
```

### 4. Verify
```bash
ls -la /mnt/HDD1/nextcloud/data/
df -h /mnt/HDD1
```

## Verification Script
```bash
#!/bin/bash
# Check if HDD1 is mounted correctly
if mount | grep -q "/mnt/HDD1"; then
    echo "✓ HDD1 is mounted"
    df -h /mnt/HDD1
else
    echo "✗ HDD1 is NOT mounted"
    echo "Run: sudo mount -a"
fi
```

## Related
- Nextcloud data is at `/mnt/HDD1/nextcloud/data/`
- Plex data is at `/mnt/HDD1/plex/`
- Media files at `/mnt/HDD1/media/`
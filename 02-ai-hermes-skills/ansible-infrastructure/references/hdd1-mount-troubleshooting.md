# HDD1 Mount Troubleshooting

## Common Issues

### Issue 1: Drive Not Mounted

**Symptom:** `/mnt/HDD1` exists but shows root filesystem stats:
```bash
df -h /mnt/HDD1
# Output: /dev/sda2 ... /mnt/HDD1 (wrong - this is rootfs)
```

**Check if drive is detected:**
```bash
lsblk -f | grep -E "(sda|sdb|HDD1)"
# Look for unmounted ext4 partition
```

**Fix fstab entry:**
```bash
# Check current fstab
cat /etc/fstab | grep HDD

# Wrong (commented out, wrong device):
#/dev/sda1 /mnt/HDD1 ext4 defaults,noatime 0 2

# Correct (uncommented, right device):
/dev/sdb1 /mnt/HDD1 ext4 defaults,noatime,nofail 0 2
```

**Key points:**
- Use `nofail` option to prevent boot hangs if drive disconnects
- Use correct device (`sdb1`, not `sda1` which is boot)
- `defaults,noatime` for performance

### Issue 2: Wrong Device in fstab

**Symptom:** Boot fails or drive mounts incorrectly

**Fix:**
```bash
# Find correct UUID/device
sudo blkid

# Update fstab with correct device
sudo sed -i '/#.*HDD1/d' /etc/fstab  # Remove old entry
echo '/dev/sdb1 /mnt/HDD1 ext4 defaults,noatime,nofail 0 2' | sudo tee -a /etc/fstab
```

### Issue 3: Permission Issues

**Symptom:** Can't write to mounted drive

**Fix ownership:**
```bash
sudo chown -R aldo:www-data /mnt/HDD1
sudo chmod -R 750 /mnt/HDD1
```

### Issue 4: Docker Volume Mount Failed

**Symptom:** Container shows empty directory or permission denied

**Check mount:**
```bash
docker inspect <container> | grep -A 5 '"Mounts"'
```

**Fix:**
```bash
# Ensure directory exists with correct permissions
sudo mkdir -p /mnt/HDD1/nextcloud/data
sudo chown -R 1000:1000 /mnt/HDD1/nextcloud  # PUID/PGID from compose
```

## Verification

```bash
# Check mount
df -hT /mnt/HDD1

# Check contents
ls -la /mnt/HDD1/

# Test write access
touch /mnt/HDD1/test && rm /mnt/HDD1/test
```

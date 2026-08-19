# Nextcloud Instance ID Mismatch Fix

## Symptom
- Nextcloud returns "Internal Server Error" on `/login`
- Error: `OCP\Files\GenericFileException`
- Logs show: `file_get_contents(/var/www/html/data/appdata_oc8smbcq3ig5/richdocuments/...): Failed to open stream`
- But actual instance ID is `oc4t3ftfs2n4`

## Root Cause
The `instanceid` in `config/config.php` doesn't match the current appdata directory name. This happens after:
- Container recreation with different DB
- Migration to new storage
- Manual instance ID changes

## Fix

### 1. Verify the Mismatch
```bash
# Check config.php instance ID
docker exec nextcloud grep "instanceid" /var/www/html/config/config.php

# Check actual appdata directory
docker exec nextcloud ls -la /var/www/html/data/ | grep appdata
```

### 2. Fix the Instance ID
```bash
# Update config.php to match actual instance
docker exec nextcloud sed -i "s/'instanceid' => 'old_id'/'instanceid' => 'new_id'/g" /var/www/html/config/config.php
```

### 3. Clear PHP Cache
```bash
docker exec nextcloud php -r "opcache_reset(); echo 'OPcache cleared';"
```

### 4. Verify
```bash
curl -sk -I https://cloud.aldof.duckdns.org/login
# Should return HTTP/2 200 (not 500)
```

## Prevention
Always verify instance ID consistency after:
- Docker compose down/up with -v
- Database restoration
- Config.php modifications

## Related
- See `nextcloud-appdata-fix.md` for appdata directory creation issues
- See `redis-caching-and-tag-pinning.md` for image pinning to avoid segfaults
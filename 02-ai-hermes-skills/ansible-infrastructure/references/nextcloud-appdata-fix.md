# Nextcloud Internal Server Error: Missing appdata_* Directory

## Symptom
- Nextcloud returns "Internal Server Error" on `/login`
- Error: `OCP\Files\GenericFileException`
- Logs show: `file_get_contents(/var/www/html/data/appdata_<instanceid>/richdocuments/remoteData/capabilities): Failed to open stream: No such file or directory`

## Root Cause
The richdocuments app attempts to cache capabilities in `data/appdata_<instanceid>/richdocuments/remoteData/`. When the instance ID changes (e.g., after DB recreation), this directory doesn't exist and throws an exception.

## Fix

### 1. Create the Missing Directory
```bash
docker exec -u www-data nextcloud-app-1 mkdir -p /var/www/html/data/appdata_oc<instanceid>/richdocuments/remoteData
```

**Get instance ID:**
```bash
docker exec nextcloud-app-1 cat /var/www/html/config/config.php | grep instanceid
```

### 2. Clear Cache (Optional)
```bash
docker exec -u www-data nextcloud-app-1 php occ maintenance:mode --on
docker exec -u www-data nextcloud-app-1 php occ maintenance:mode --off
```

## Prevention

When deploying Nextcloud via Ansible:
1. Ensure the data volume is properly mounted
2. The `data` directory must exist and be owned by www-data
3. Instance ID is set during `occ maintenance:install`

## Related Issues
- Stale appdata directories from previous deployments
- Richdocuments app trying to access non-existent cached files
- Permission issues when creating directories manually (use `-u www-data`)
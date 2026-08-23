#!/bin/bash
# nextcloud-db-backup.sh — nightly mysqldump of the Nextcloud MariaDB.
# Usage: nextcloud-db-backup.sh <core-infra-dir>
# The cron entry passes __CORE_INFRA__ as $1 (rendered by install.sh).
set -euo pipefail

CORE_INFRA="${1:-${HOME}/dev/01-core-infra}"
if [ ! -d "$CORE_INFRA" ]; then
    echo "ERROR: core-infra dir not found: $CORE_INFRA" >&2
    exit 2
fi

CONTAINER="nextcloud-db"
RETENTION_DAYS=7
STAMP=$(date '+%Y-%m-%d_%H%M%S')
BACKUP_DIR="${CORE_INFRA}/backups/nextcloud-db"
mkdir -p "$BACKUP_DIR" "${CORE_INFRA}/logs"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    log "ERROR: container $CONTAINER not running — aborting"
    exit 1
fi

OUT="$BACKUP_DIR/nextcloud-db_$STAMP.sql.gz"
log "Dumping $CONTAINER -> $OUT"
docker exec "$CONTAINER" sh -c \
    'exec mariadb-dump --single-transaction --quick --routines --triggers -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' \
    | gzip > "$OUT"

SIZE=$(stat -c%s "$OUT")
if [ "$SIZE" -lt 10000 ]; then
    log "ERROR: dump suspiciously small (${SIZE} bytes) — keeping file but failing"
    exit 1
fi
log "Dump OK: $OUT ($(( SIZE / 1024 )) KiB)"

find "$BACKUP_DIR" -name 'nextcloud-db_*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
log "Retention applied (> ${RETENTION_DAYS}d removed)"

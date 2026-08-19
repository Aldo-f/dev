# Deezer + Nextcloud Integration

## Configuration

The Deezer downloader script (`~/scripts/deezer/scripts/deezer.py`) can be configured to download directly into Nextcloud's data directory.

### Environment Configuration

Create `/home/aldo/.config/deezer/.env`:

```bash
DEEZER_MUSIC_SEED="/mnt/HDD1/nextcloud/data/aldo/files/Media/music"
```

**⚠️ Case sensitivity matters!** The user's Nextcloud directory structure uses `Media/music` (uppercase M), not `media/music` (lowercase). Using the wrong case will create a non-existent directory and cause permission errors.

This is read automatically by the script on startup (loads `.env` before argument parsing).

### Directory Setup

The target directory must exist and be writable by the Nextcloud container user (`www-data`):

```bash
sudo mkdir -p /mnt/HDD1/nextcloud/data/aldo/files/media/music
sudo chown -R www-data:www-data /mnt/HDD1/nextcloud/data/aldo/files/media
sudo chmod -R 775 /mnt/HDD1/nextcloud/data/aldo/files/media
```

### Post-Download Scan

After downloads complete, trigger a Nextcloud file scan so new tracks appear in the UI:

```bash
docker exec -u www-data nextcloud php occ files:scan --path=aldo/files/media/music
```

This can be automated in a wrapper script or cron job.

## Usage Examples

```bash
# Download a playlist directly to Nextcloud
~/scripts/deezer/scripts/deezer.py download-playlist "https://www.deezer.com/nl/playlist/13743997181" --workers 4

# The --out flag is optional (reads from DEEZER_MUSIC_SEED env)
~/scripts/deezer/scripts/deezer.py download-flow --limit 50
```

## Common Issues

| Issue | Resolution |
|-------|------------|
| Permission denied on write | Directory not owned by www-data; fix with chown/chmod above |
| Files not showing in Nextcloud | Run `occ files:scan` on the target path |
| Tracks fail with "code 2002" | Free tier limitation — premium tracks unavailable without paid account |
| SSL/TLS timeout on CDN | Retry; transient network issue with `cdnt-stream.dzcdn.net` |
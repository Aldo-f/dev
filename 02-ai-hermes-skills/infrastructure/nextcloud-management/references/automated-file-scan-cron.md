# Automated `occ files:scan` scheduling (cron + logrotate)

Production pattern for keeping Nextcloud's file index in sync for ALL users when
files are placed on disk out-of-band (rsync, mounts) — deployed idempotently via
Ansible on the host running the container.

## The composed pieces

1. **Bash script** at `/usr/local/bin/nextcloud-sync-all.sh`:
   - `set -uo pipefail`
   - Health check BEFORE scanning: `RUNNING=$(docker inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null)`; if not `true`, log a WARN and `exit 0` (so cron never sees an error for a legitimately-down container).
   - Run the scan as the in-container web user (IMPORTANT — must match the OCC user, not root):
     `docker exec --user www-data "$CONTAINER" php occ files:scan --all`
   - Capture `RC`, log INFO success / ERROR failure, always `exit 0`.
   - Timestamped `log()` helper appends to `/var/log/nextcloud-sync.log`.

2. **Cron** — hourly as root via Ansible `cron` module: `0 * * * *`, `user: root`. Idempotent: `state: present` only touches the crontab if the entry is missing.

3. **Logrotate** at `/etc/logrotate.d/nextcloud-sync`:
   ```
   /var/log/nextcloud-sync.log {
       weekly
       rotate 4
       compress
       delaycompress
       missingok
       notifempty
       create 0640 www-data adm
   }
   ```
   `missingok` + `notifempty` make it graceful on empty/missing logs. Validate with
   `sudo logrotate --debug /etc/logrotate.d/nextcloud-sync`.

## Testing the playbook

- `ansible-playbook --syntax-check`, then `--check` (dry-run).
- First deploy → all tasks `changed`. **Re-run the same playbook → `changed=0` proves idempotency.**
- Functional: `sudo <script>` with container up → bytes `Starting files:scan…`, `Finished … (success)`.
- A real `files:scan --all` output ends with the folders/files/new/updated/removed/errors summary per user — that's the success signal (0 errors for a clean run).

## Ansible pitfall (caught by dry-run)

Use the `copy` module to write inline content you MUST name the destination with
**`dest:`** — not `path:`. `copy` with `path:` fails at runtime with
`"msg": "dest is required"`. `src:`/`dest:` for file copies, `dest:` + `content:`
for inline writes.

## Repo placement

- Implemented as a proper Ansible role: `ansible/roles/nextcloud-sync/` containing:
  - `defaults/main.py` - variables (container name, paths, cron schedule)
  - `tasks/main.yml` - three tasks: deploy health-checked script, install logrotate config, install hourly cron job
- Wired into `ansible/playbooks/site.yml` - runs automatically after the `containers` role on every `./install.sh` or `ansible-playbook site.yml`
- No standalone playbook needed; the role provides the idempotent deployment
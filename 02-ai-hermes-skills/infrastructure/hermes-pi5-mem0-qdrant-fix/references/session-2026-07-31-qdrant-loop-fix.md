# Session Reference: Fixing Hermes WebUI restart loop on Pi 5 (2026-07-31)

## Symptoms
- Browser showed "CONNECTION LOST" every second.
- `journalctl -u app-hermes-webui.service` displayed repeating pattern:
  ```
  Started app-hermes-webui.service - Hermes WebUI daemon...
  Stopping app-hermes-webui.service - Hermes WebUI daemon...
  app-hermes-webui.service: Deactivated successfully.
  ```
  with ~5 second intervals between start and stop.
- `systemctl status qdrant.service` showed:
  ```
  Active: activating (auto-restart) (Result: exit-code) since ...
  Main PID: XXXXX (code=exited, status=203/EXEC)
  qdrant.service: Unable to locate executable '/home/aldo/.local/bin/qdrant': No such file or directory
  ```
  OR (after binary reinstalled):
  ```
  qdrant.service: Unable to locate executable '/home/aldo/.local/bin/qdrant': No such file or directory
  qdrant.service: Failed at step EXEC spawning /home/aldo/.local/bin/qdrant: No such file or directory
  ```
  with restart counter increasing (reached 173).

## Root Cause
1. Qdrant binary missing from `~/.local/bin/qdrant` (removed during toolchain reset).
2. Official Qdrant binaries (Docker or static `aarch64-unknown-linux-musl`) crash on Pi 5 due to jemalloc incompatibility with 16 KB page size:
   ```
   <jemalloc>: Unsupported system page size
   memory allocation of ... failed
   ```
3. `app-hermes-webui.service` had `Requires=qdrant.service` — when qdrant failed, systemd stopped webui too.
4. WebUI unit's `Restart=on-failure` + `RestartSec=5` created a stop/start loop every ~5s.

## Fix Steps Applied
1. **Stop and disable qdrant.service** (can't run on Pi 5):
   ```bash
   sudo systemctl stop qdrant.service
   sudo systemctl disable qdrant.service
   sudo systemctl reset-failed qdrant.service
   ```
2. **Confirm mem0 uses embedded Qdrant** (already the case via plugin defaults; corrected config):
   ```json
   {
     "mode": "oss",
     "user_id": "aldo",
     "agent_id": "hermes",
     "oss": {
       "llm": {
         "provider": "openai",
         "config": {
           "api_key": "<freellmapi-key>",
           "openai_base_url": "http://localhost:3001/v1",
           "model": "gemini-2.5-flash-lite"
         }
       },
       "embedder": {
         "provider": "ollama",
         "config": {
           "ollama_base_url": "http://localhost:11434",
           "model": "nomic-embed-text",
           "embedding_dims": 768
         }
       },
       "vector_store": {
         "provider": "qdrant",
         "config": {
           "path": "/home/aldo/.hermes/mem0_qdrant",
           "collection_name": "mem0"
         }
       }
     }
   }
   ```
   (Note: ensure `path` expands to `/home/aldo/.hermes/mem0_qdrant` and directory exists.)
3. **Edit WebUI systemd unit** to remove qdrant dependency:
   ```bash
   sudo nano /etc/systemd/system/app-hermes-webui.service
   ```
   Changed:
   ```
   After=network.target xvfb.service qdrant.service
   Wants=xvfb.service
   Requires=qdrant.service
   ```
   To:
   ```
   After=network.target xvfb.service
   Wants=xvfb.service
   ```
   (Removed `qdrant.service` from After and deleted Requires line.)
4. **Reload and restart services**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart app-hermes-webui.service
   systemctl --user restart hermes-gateway.service
   ```
5. **Verification**:
   - `systemctl is-active app-hermes-webui.service` → active
   - `curl -s http://127.0.0.1:8787/health` → HTTP 200
   - `journalctl -u app-hermes-webui.service --since "15:10"` shows zero "Stopping" lines after 15:10.
   - `systemctl --user is-active hermes-gateway.service` → active
   - `systemctl is-active qdrant.service` → inactive
   - Mem0 E2E test passes (add + search via embedded Qdrant + Ollama embedder).

## Notes
- The `mem0.json` had briefly been set to use the `holographic` provider during testing; restored to `qdrant` with path-based config.
- Both Telegram gateway (PID 1218, `hermes-gateway.service`) and WebUI now share the same embedded mem0 store.
- No Docker container for `hermes-webui` exists; the restart loop was purely systemd‑service driven.

## Related Skills
- `hermes-pi5-mem0-qdrant-fix` – this skill
- `self-hosted-memory-backends` – general mem0 setup (note: avoid qdrant server on Pi 5)
- `hermes-webui-service` – managing the WebUI unit (ensure it lacks `Requires=qdrant.service`)
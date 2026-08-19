---
name: hermes-pi5-mem0-qdrant-fix
category: infrastructure
description: Fix Hermes UI loop and mem0 on Pi 5 due to qdrant/jemalloc.
---
# Hermes WebUI & mem0 on Raspberry Pi 5 – Qdrant Workaround

## Problem
On Raspberry Pi 5 (kernel with 16 KB page size), the official Qdrant binaries (Docker or static `qdrant-aarch64-unknown-linux-musl.tar.gz`) abort immediately with:
```
<jemalloc>: Unsupported system page size
memory allocation of ... failed
```
If `app-hermes-webui.service` contains `Requires=qdrant.service`, each qdrant crash causes systemd to stop the WebUI, and its `Restart=on-failure` triggers a tight ~5 second stop/start loop, manifesting as “CONNECTION LOST” every few seconds in the browser.

Mem0 configured for host/port Qdrant also fails with connection refused.

## Solution
1. **Do not run a Qdrant server** on Pi 5. Disable and stop `qdrant.service`.
2. **Use Mem0 in OSS mode with embedded Qdrant** (path‑based client).  
   Example `~/.hermes/mem0.json`:
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
3. **Remove `Requires=qdrant.service` from the WebUI systemd unit**.  
   Edit `/etc/systemd/system/app-hermes-webui.service`:
   ```
   [Unit]
   Description=Hermes WebUI daemon
   After=network.target xvfb.service
   Wants=xvfb.service
   # (Requires=qdrant.service and Wants=xvfb.service removed)
   [Service]
   Type=simple
   User=aldo
   WorkingDirectory=/home/aldo/dev/02-ai-hermes-webui
   ExecStart=/home/aldo/.hermes/hermes-agent/venv/bin/python /home/aldo/dev/02-ai-hermes-webui/server.py
   Restart=on-failure
   RestartSec=5
   Environment=HERMES_HOME=/home/aldo/.hermes
   Environment=HERMES_WEBUI_HOST=0.0.0.0
   Environment=DISPLAY=:99
   Environment=MEM0_TELEMETRY=False
   [Install]
   WantedBy=multi-user.target
   ```
   Then run `sudo systemctl daemon-reload && sudo systemctl restart app-hermes-webui.service`.
4. **Restart the Hermes gateway** (systemd --user) so it picks up the updated mem0 config:
   ```
   systemctl --user restart hermes-gateway.service
   ```
5. **Verify**:
   - `systemctl is-active app-hermes-webui.service` → active
   - `curl -s http://127.0.0.1:8787/health` → `{"status":"ok",...}` (HTTP 200)
   - `systemctl --user is-active hermes-gateway.service` → active
   - `systemctl is-active qdrant.service` → inactive (or disabled)
   - Mem0 test:
     ```python
     from mem0 import Memory
     m = Memory.from_config(<see‑above‑json>)
     m.add(messages=[{"role":"user","content":"test fact"}], user_id="test", agent_id="hermes", infer=False)
     res = m.search(query="test fact", filters={"user_id":"test"}, limit=1)
     print("mem0 embedded E2E:", "OK" if res.get("results") else "FAIL")
     ```
     should succeed.

## Why This Works
- Embedded Qdrant uses the local file‑system via `qdrant-client` Python library, which does not depend on the jemalloc‑bundled binary and runs fine on Pi 5.
- By removing the hard dependency on `qdrant.service`, the WebUI no longer stops when Qdrant fails; it runs independently and relies only on the embedded store already used by Mem0.
- Both the Telegram‑linked gateway and the WebUI share the same Mem0 configuration, so memory is shared across interfaces.

## Troubleshooting
- If you still see “connection refused” from Mem0, double‑check that `mem0.json` points to `provider: qdrant` with a `path` (not host/port).
- Ensure the directory `~/.hermes/mem0_qdrant` exists and is writable by the `aldo` user.
- Check journal logs: `journalctl -u app-hermes-webui.service -f` and `journalctl --user -u hermes-gateway.service -f`.
- Remember that the Hermes agent process (gateway) and the WebUI are separate services; both must be restarted after changing `mem0.json`.

## Related Skills
- `self-hosted-memory-backends` – general Mem0/OSS setup (note: this workaround supersedes the Docker/Qdrant‑server advice for Pi 5).
- `hermes-webui-service` – manage the WebUI systemd unit (ensure it lacks `Requires=qdrant.service`).

---
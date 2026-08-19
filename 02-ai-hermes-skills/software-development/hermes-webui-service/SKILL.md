---
name: hermes-webui-service
description: Manage Hermes WebUI start/stop/status and health checks.
trigger: Use when you need to start, stop, check status, or diagnose the Hermes WebUI service.
---
# Hermes WebUI Service Management

This skill provides a class‑level guide for operating the Hermes WebUI server on a Linux host (e.g., Raspberry Pi). It abstracts the fact that the WebUI is **not** a systemd unit but is launched via the repository's `ctl.sh` script, which wraps the Python `server.py` process.

## Typical workflow
Manage the Hermes WebUI via Docker Compose (preferred method per user infrastructure):

### Via Docker Compose (preferred)
```bash
cd ~/dev/02-ai-hermes-webui
docker compose up -d hermes-webui    # Start service
docker compose ps                    # Check status
docker compose logs hermes-webui     # View logs
docker compose down hermes-webui     # Stop service
```

### Via ctl.sh (alternative for direct host execution)
```bash
cd ~/dev/02-ai-hermes-webui
./ctl.sh start   # launches server.py in background
./ctl.sh status
./ctl.sh stop
```

**Health endpoint** (same for both methods)
```bash
curl -s http://127.0.0.1:8787/health
```
Returns JSON with keys `status`, `sessions`, `active_streams`, `active_runs`, etc. A non‑200 HTTP status indicates the service is not running.

**Verify LAN reachability**
From another host on the LAN (e.g., `http://192.168.0.5:8787/`), a `302` redirect to the sign‑in page is expected, followed by a `200` on the health endpoint.

## Bare-metal mode (WebUI agent can run docker, ansible, sudo, etc.)
By default the WebUI's chat agent has a **restricted** toolset — it can read sessions / settings / cron history, but cannot run `docker`, `ansible-playbook`, or arbitrary shell. To give the chat agent full bare-server access (so prompts like "run `docker ps` and report" actually work), set five gateway keys in `~/.hermes/config.yaml`.

**The agent cannot patch `~/.hermes/config.yaml` directly** — `patch`/`write_file` on that path is blocked by a security guard. Always use the `hermes config set` CLI:

```bash
HERMES_CFG=/home/aldo/.hermes/hermes-agent/venv/bin/hermes
$HERMES_CFG config set gateway.enabled_toolsets '["terminal","file","web","delegation","cron","memory","skills","computer_use"]'
$HERMES_CFG config set gateway.allow_sudo true
$HERMES_CFG config set gateway.allow_docker true
$HERMES_CFG config set gateway.container_command_timeout 600
$HERMES_CFG config set gateway.expose_shell_to_chat true
$HERMES_CFG config get gateway          # verify
docker restart hermes-webui
```

Then health-loop until `healthy` and probe the chat with a fresh session via the API (see `references/session_20260818_bare-metal-mode-setup.md` for the exact verified commands, including the non-obvious endpoint `POST /api/session/new`).

### The `localhost:3001` trap (model base_url)
The WebUI image is built with `model.base_url: http://localhost:3001/v1` pointing at the freellmapi router. Inside the container, `localhost` resolves to the container itself — the freellmapi container on `traefik_net` is **not** reachable that way. Chat will fail with `API call failed after 3 retries: Connection error` even though `curl http://freellmapi:3001/v1/models` from inside the container returns 200/401. Fix:

```bash
$HERMES_CFG config set model.base_url 'http://freellmapi:3001/v1'
docker restart hermes-webui
```

The matching `api_key` env var is named `HERMES_CUSTOM_LOCALHOST_3001_API_KEY` — if you change `base_url`, ensure the env var name still corresponds, otherwise the agent gets 401 from freellmapi even with the right URL. Check `grep -E 'base_url|api_key' ~/.hermes/config.yaml`.

#### ⚠️ The `custom_providers` override trap (CRITICAL — discovered 2026-08-18)
**Patching `model.base_url` alone is a no-op.** The `custom_providers:` list at the bottom of `config.yaml` contains its own `FreeLLM` entry with its own `base_url` and `key_env`, and **that entry takes precedence** for chat requests. After running only `hermes config set model.base_url`, the request dump at `/home/hermeswebui/.hermes/sessions/request_dump_*.json` will still show `"url": "http://localhost:3001/v1/chat/completions"`.

Verify with:
```bash
grep -nE "localhost:3001|freellmapi:3001" ~/.hermes/config.yaml
# You should see TWO freellmapi:3001 hits (top-level + custom_providers),
# NOT three+ (any leftover localhost:3001 means the custom_providers entry
# wasn't patched).
```

The agent **cannot** patch `custom_providers[*]` via `hermes config set` — list items aren't scalar keys. The agent's `patch`/`write_file` on `~/.hermes/config.yaml` is also blocked by the security guard. The user must run `sed` themselves, e.g.:

```bash
sed -i 's|http://localhost:3001/v1|http://freellmapi:3001/v1|; \
        s|HERMES_CUSTOM_LOCALHOST_3001_API_KEY|HERMES_CUSTOM_FREELLMAPI_3001_API_KEY|' \
        ~/.hermes/config.yaml
docker restart hermes-webui
```

The same sed also aligns the `key_env` name to match the new base_url host. Verify with `grep -nE "freellmapi:3001|FREELLMAPI_3001" ~/.hermes/config.yaml` — expect ≥ 3 hits.

### Sudo binary missing in container
The Python base image does NOT include `sudo`. The container runs as `uid=0` already (so root-level commands work without sudo), but if you ever drop to the `hermeswebui` user and still need to escalate, install sudo once:

```bash
docker exec -u root hermes-webui bash -c \
  'apt-get update -qq && apt-get install -y -qq sudo'
```

## Common pitfalls & fixes
- **Port 8787 already in use**: The WebUI binds to port 8787 by default. If `docker compose up` fails with `bind: address already in use`, check for a stale Python process running `server.py` directly on the host:
  ```bash
  ss -tlnp | grep 8787
  kill <PID>
  docker compose up -d hermes-webui
  ```
- **Missing systemd unit**: Users often look for `app-hermes-webui.service`. The correct control is Docker Compose or `ctl.sh`; there is no systemd service unless the user creates a custom unit.
- **Port binding**: Ensure `HERMES_WEBUI_HOST=0.0.0.0` in `.env` (or `docker-compose.yml`) so the UI is reachable from other LAN devices.
- **Stale process after reboot**: Docker containers survive reboots with `restart: unless-stopped`. After a reboot, `docker compose ps` will show the status.
- **Log location**: 
  - Docker: `docker compose logs hermes-webui`
  - Host `ctl.sh`: `${HOME}/.hermes/webui.log`
- **WebUI agent cannot reach freellmapi despite service being up**: see the `localhost:3001` trap above — `base_url` must use the container DNS name on `traefik_net`, not `localhost`.
- **Chat returns `API call failed after 3 retries: Connection error`** but `curl http://freellmapi:3001/v1/models` from inside the container works → check both the `model.base_url` AND the `custom_providers[FreeLLM].base_url`. Patching only the top-level is a no-op; see "The custom_providers override trap" below.
- **Patched `model.base_url` but chat still hits `localhost:3001`** → request dump shows `"url": "http://localhost:3001/v1/chat/completions"`. The `custom_providers[FreeLLM].base_url` overrides it. The agent cannot patch list items — user must `sed` the file directly.
- **401 from freellmapi despite correct URL** → the env var name `HERMES_CUSTOM_<baseurl-host>_<port>_API_KEY` must match the new `base_url` host. For `freellmapi:3001` use `HERMES_CUSTOM_FREELLMAPI_3001_API_KEY`. Add it to `~/.hermes/.env` and restart.
- **Tool-call requests return `429 routing_exhausted` from freellm**: freellm's routed model lacks tool-calling capability. Configure a tool-capable model in freellmapi or bypass the waterfall for tool-required prompts.

## References
- See `references/session_20260729_hermes-webui-health.md` for the exact commands and output observed during the session where the health endpoint was verified after a manual reboot.
- See `references/session_20260729_hermes-webui-reboot-fix.md` for reboot recovery workflow.
- See `references/session_20260805_port-8787-conflict-fix.md` for diagnosing 502 Bad Gateway caused by a stale host process occupying port 8787.
- See `references/session_20260818_bare-metal-mode-setup.md` for the verified steps to enable docker / sudo / ansible execution from the WebUI chat agent (gateway toolsets, base_url fix, sudo install, API endpoints).
- See `references/session_20260818_custom_providers-override.md` for the deeper trap discovered same session: `custom_providers[FreeLLM].base_url` overrides `model.base_url`, and the agent cannot patch list items in `~/.hermes/config.yaml`.

## Agent capability boundary (for Hermes agents operating this skill)
- ✅ Agent CAN: install `sudo` in the container, write `~/.hermes/.env`, run `hermes config set <scalar_key>`, `docker restart`, `docker exec`, `curl` probes, health-loop polls.
- ❌ Agent CANNOT: `patch` or `write_file` on `~/.hermes/config.yaml` (security guard). Address scalar keys with `hermes config set`. List items (`custom_providers[*]`, role lists, etc.) require the user to `sed`/`vim` the file — surface the exact one-liner.
- ✅ Agent CAN read `~/.hermes/config.yaml` and inspect request dumps under `~/.hermes/sessions/request_dump_*.json` to verify which `base_url` is actually being hit.

# Session 2026-08-18 — `custom_providers` override trap

## Symptom
After patching `model.base_url` from `http://localhost:3001/v1` to `http://freellmapi:3001/v1` via `hermes config set` and restarting the container, chat still fails with:

```
API call failed after 3 retries: Connection error.
```

A request dump at `~/.hermes/sessions/request_dump_<sid>_<ts>_<rid>.json` confirms the agent is still hitting the old URL:

```json
{
  "request": {
    "method": "POST",
    "url": "http://localhost:3001/v1/chat/completions",
    ...
  }
}
```

Yet from inside the container:

```bash
docker exec hermes-webui curl -sv http://freellmapi:3001/v1/models
# → Connected to freellmapi (172.18.0.10) port 3001
# → HTTP/1.1 401 Unauthorized
```

…returns 401 (connection works, auth is the separate issue). So the WebUI process is talking to a different URL than the one in `model.base_url`.

## Root cause
`~/.hermes/config.yaml` has TWO places that store the model URL:

```yaml
model:
  provider: custom
  base_url: http://freellmapi:3001/v1          # ← patched
  api_key: ${HERMES_CUSTOM_LOCALHOST_3001_API_KEY}

custom_providers:
  - name: FreeLLM
    base_url: http://localhost:3001/v1          # ← STILL localhost, NOT patched
    key_env: HERMES_CUSTOM_LOCALHOST_3001_API_KEY
    model: auto
    models: [...]
```

For chat requests, the `custom_providers` FreeLLM entry takes precedence over the top-level `model.base_url`. `hermes config set model.base_url …` only updates the top-level; it does not touch `custom_providers[*]`.

## Verify
```bash
grep -nE "localhost:3001|freellmapi:3001" ~/.hermes/config.yaml
# Expected after partial fix:
#   9:  base_url: http://freellmapi:3001/v1
#   241:    base_url: http://localhost:3001/v1          ← still wrong
#   242:    key_env: HERMES_CUSTOM_LOCALHOST_3001_API_KEY  ← name mismatch
#
# Expected after full fix:
#   9:  base_url: http://freellmapi:3001/v1
#   241:    base_url: http://freellmapi:3001/v1
#   242:    key_env: HERMES_CUSTOM_FREELLMAPI_3001_API_KEY
```

## Fix
The Hermes agent cannot patch list items via `hermes config set` — that CLI only addresses scalar top-level keys. The agent's `patch` / `write_file` on `~/.hermes/config.yaml` is also blocked by the security guard ("Agent cannot modify security-sensitive configuration"). The user must run `sed` themselves:

```bash
sed -i 's|http://localhost:3001/v1|http://freellmapi:3001/v1|; \
        s|HERMES_CUSTOM_LOCALHOST_3001_API_KEY|HERMES_CUSTOM_FREELLMAPI_3001_API_KEY|' \
        ~/.hermes/config.yaml

docker restart hermes-webui
```

The single sed updates:
- `model.base_url` (was already correct, harmless no-op)
- `custom_providers[FreeLLM].base_url` (the real fix)
- `custom_providers[FreeLLM].key_env` (must align with the new host so the env var `HERMES_CUSTOM_FREELLMAPI_3001_API_KEY` is read)
- Any other occurrences that follow the same pattern

Then verify auth: add the key to `~/.hermes/.env`:

```bash
grep -q 'HERMES_CUSTOM_FREELLMAPI_3001_API_KEY' ~/.hermes/.env \
  || echo 'HERMES_CUSTOM_FREELLMAPI_3001_API_KEY=freellmapi-f7c7b8542d6904afe2c39640de28b0f797f47d5f21ff6723' >> ~/.hermes/.env

docker restart hermes-webui
```

## Agent capability boundary
This trap exposes an asymmetric capability boundary the agent must respect:
- ✅ Agent can run `hermes config set <scalar>` for scalar top-level keys (`model.base_url`, `gateway.*`, `agent.*`, etc.).
- ✅ Agent can write `~/.hermes/.env` to add new env vars.
- ✅ Agent can `docker exec` to install software inside the container.
- ❌ Agent cannot patch `custom_providers[*]`, role lists, or any list-valued config section via `hermes config set`.
- ❌ Agent cannot `patch` / `write_file` on `~/.hermes/config.yaml` — security guard blocks it.

When an agent discovers this trap, the right move is: stop, surface the exact one-liner the user needs to run, and offer to verify after they do.

## Related
- See also `session_20260818_bare-metal-mode-setup.md` for the broader bare-metal-mode setup and the WebUI chat API endpoints used to verify end-to-end.
- General pitfall list in SKILL.md covers the same symptom under "Chat returns `API call failed after 3 retries`".

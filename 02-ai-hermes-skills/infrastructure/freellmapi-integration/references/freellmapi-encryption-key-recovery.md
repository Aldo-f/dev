# freellmapi — ENCRYPTION_KEY & Decrypt Errors Reference

## The Problem
When freellmapi container is recreated with a different `ENCRYPTION_KEY` (or auto-generates one), all previously stored provider API keys become unreadable.

### Symptoms
- Logs show `decrypt-error:N` for multiple providers:
  ```
  google/gemini-3.1-flash-lite: 12 key(s) — decrypt-error:12
  agnes/agnes-2.0-flash: 3 key(s) — decrypt-error:3
  openrouter/cohere/north-mini-code:free: 9 key(s) — decrypt-error:9
  groq/openai/gpt-oss-120b: 2 key(s) — decrypt-error:2
  ollama/gpt-oss:120b: 9 key(s) — decrypt-error:5, cooldown:4
  ...
  ```
- Router falls back to keyless providers (ollama) or fails requests

### Root Cause
- Provider API keys are stored encrypted in SQLite DB (`freeapi.db`) in Docker volume `02-ai-freellm_freellmapi-data`
- Encryption uses `ENCRYPTION_KEY` from container env
- If container gets new key (or generates one), old keys cannot be decrypted
- **The vault (`freellmapi-credentials.yml`) ONLY contains the encryption key and basic config — NOT provider API keys**

---

## Recovery Procedure

### 1. Ensure correct ENCRYPTION_KEY in .env
```bash
# Copy from backup (contains correct key)
cp ~/backups/env/02-ai-freellm.env ~/dev/02-ai-freellm/.env

# Verify .env has correct key
grep ENCRYPTION_KEY ~/dev/02-ai-freellm/.env
# Should show: ENCRYPTION_KEY=4ba635a9169b38724eee7b774797d7ed8bd55e696f4027b56a05fe3690a16995
```

### 2. Remove stale encryption-key files
```bash
# Local file
rm -f ~/dev/02-ai-freellm/.encryption-key

# Docker volume file (requires sudo)
sudo rm -f /var/lib/docker/volumes/02-ai-freellm_freellmapi-data/_data/.encryption-key
```

### 3. Recreate container
```bash
cd ~/dev/02-ai-freellm
docker compose up -d --force-recreate freellmapi
```

### 4. Verify container uses correct key
```bash
docker inspect 02-ai-freellm-freellmapi-1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep ENCRYPTION_KEY
# Must show: ENCRYPTION_KEY=4ba635a9169b38724eee7b774797d7ed8bd55e696f4027b56a05fe3690a16995
```

### 5. Re-enter provider API keys via web UI
1. Open: `http://192.168.0.5:3001`
2. Log in / create admin
3. Go to Providers / Keys section
4. Re-enter each provider's API key:
   - **Google (Gemini)**: one or more API keys
   - **OpenRouter**: API key
   - **Groq**: API key
   - **Cerebras**: API key
   - **Agnes**: API key (if applicable)
   - **Opencode**: API key (if applicable)
5. Save each — they'll be encrypted with the new correct key

### 6. Verify decrypt errors resolved
```bash
docker logs 02-ai-freellm-freellmapi-1 2>&1 | grep "decrypt-error"
# Should return NO matches (exit code 1)
# Or: docker logs ... | grep -c "decrypt-error" → should be 0
```

---

## Prevention

### Ansible playbook should:
1. Render `.env` from vault BEFORE deploying container
2. Ensure no stale `.encryption-key` files exist
3. Set `ENCRYPTION_KEY` in container env explicitly (not auto-generated)

### Current vault contents (`freellmapi-credentials.yml`):
```yaml
vault_freellmapi_encryption_key: "4ba635a9169b38724eee7b774797d7ed8bd55e696f4027b56a05fe3690a16995"
vault_freellmapi_port: "3001"
vault_freellmapi_host_bind: "0.0.0.0"
vault_freellmapi_analytics_retention_days: "90"
vault_freellmapi_analytics_max_rows: "100000"
```

**Missing from vault:** Provider API keys (Gemini, OpenRouter, Groq, etc.) — these must be entered manually via UI.

---

## Diagnostic Commands

```bash
# Check container env
docker inspect 02-ai-freellm-freellmapi-1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep ENCRYPTION_KEY

# Count decrypt errors
docker logs 02-ai-freellm-freellmapi-1 2>&1 | grep -c "decrypt-error"

# List all decrypt errors
docker logs 02-ai-freellm-freellmapi-1 2>&1 | grep "decrypt-error"

# Check health
curl -s http://localhost:3001/api/health
# {"error":{"message":"Authentication required","type":"authentication_error"}} = healthy
```
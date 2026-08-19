# Hermes WebUI: Pre-built Image (2026-08-14)

## CRITICAL: Never Build from Source

The Hermes WebUI Dockerfile contains a setuptools restriction that **blocks editable installs**:

```
RuntimeError: Building wheels or sdists for hermes-agent is not supported.
Hermes is distributed via the shell installer, Docker image, or Nix.
```

**Always use the pre-built image:**
```yaml
services:
  hermes-webui:
    image: ghcr.io/nesquena/hermes-webui:latest  # ← NEVER use build:
```

## Why Source Build Fails

1. The container mounts `/home/aldo/.hermes/hermes-agent` (source tree)
2. `docker_init.bash` tries `uv pip install -e /app/hermes-agent`
3. setuptools rejects editable installs with the error above
4. The build process hits a dead end even though the image contains all dependencies

## Correct Template

```yaml
# templates/infra/02-ai-hermes-webui/docker-compose.yml
services:
  hermes-webui:
    image: ghcr.io/nesquena/hermes-webui:latest
    container_name: hermes-webui
    restart: unless-stopped
    expose:
      - "8787"
    networks:
      - traefik_net
    volumes:
      - /home/aldo/.hermes:/home/hermeswebui/.hermes
      - /home/aldo/dev:/workspace
    environment:
      - HERMES_WEBUI_HOST=0.0.0.0
      - HERMES_WEBUI_PORT=8787
      - HERMES_WEBUI_STATE_DIR=/home/hermeswebui/.hermes/webui
      - HERMES_WEBUI_PASSWORD=${HERMES_WEBUI_PASSWORD}
      - HERMES_WEBUI_DEFAULT_WORKSPACE=/workspace
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8787/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s  # ← Pre-built image needs ~90s to initialize

networks:
  traefik_net:
    external: true
```

## Key Differences from Build Approach

| Aspect | Build (FAILS) | Pre-built (WORKS) |
|--------|---------------|-------------------|
| Image source | Local Dockerfile | `ghcr.io/nesquena/hermes-webui:latest` |
| Startup time | ~2 min + build | ~90s |
| Dependencies | Installed from source | Pre-installed |
| Source mount | Required | Optional (read-only) |

## Deployment Steps

```bash
# 1. Create runtime directory
mkdir -p /home/aldo/dev/02-ai-hermes-webui

# 2. Copy template (from ansible-infrastructure skill)
cp templates/infra/02-ai-hermes-webui/docker-compose.yml \
   /home/aldo/dev/02-ai-hermes-webui/

# 3. Deploy
cd /home/aldo/dev/02-ai-hermes-webui
docker compose up -d

# 4. Wait for health (60s start_period)
sleep 70
docker ps --filter name=hermes-webui

# 5. Verify
curl -s https://web.hermes.dev.aldof.duckdns.org/health
```

## Related Pitfalls

- **__HOME__ placeholder**: Docker Compose doesn't expand `__HOME__` — use absolute paths
- **Container name mismatch**: Nextcloud runs as `05-media-nextcloud-app-1`, not `nextcloud`
- **Verification script**: Update `verify_deployment.py` to use correct container names
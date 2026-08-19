# Example: Exposing Hermes WebUI via Traefik

This reference documents the specific steps taken to expose the Hermes WebUI at `web.hermes.dev.aldof.duckdns.org` via Traefik in the Aldo-f/home infrastructure.

## Context

The Hermes WebUI runs in the `~/dev/02-ai-hermes-webui/` directory and is accessible locally at `http://127.0.0.1:8787` (or `http://0.0.0.0:8787` for LAN access). The Traefik reverse proxy runs in `~/dev/04-network-traefik/` and is configured via `routes.yml`.

## Changes Made (CORRECT APPROACH - Container Name Routing)

Added the following routers and service to `routes.yml`:

```yaml
    hermes-http:
      rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
      entryPoints:
        - web
      middlewares:
        - https-redirect
        - ipAllowList
      service: hermes-webui

    hermes:
      rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
      entryPoints:
        - websecure
      service: hermes-webui
      tls:
        certResolver: myresolver
      middlewares:
        - ipAllowList

  # ... under the services section ...
  hermes-webui:
    loadBalancer:
      servers:
        - url: "http://hermes-webui:8787"
```

### Notes on the configuration:
- The `hermes-http` router listens on the `web` entrypoint (port 80) and redirects to HTTPS via the `https-redirect` middleware.
- The `hermes` router listens on the `websecure` entrypoint (port 443) and terminates TLS using the `myresolver` certificate resolver (Let's Encrypt).
- Both routers point to the `hermes-webui` service.
- **CRITICAL**: The `hermes-webui` service forwards traffic to `http://hermes-webui:8787`, which uses the **Docker container name** resolved via Docker's internal DNS on the shared `traefik_net` network. This is stable and doesn't require external routing.

> **Previous incorrect approach (FIXED)**: Used hardcoded IP `http://192.168.0.5:8787` which breaks when host IP changes.

## Deployment Requirements

For this to work, Hermes WebUI must be deployed as a **Docker container** on the `traefik_net` network (not as a systemd service on the host). See `ansible-infrastructure/references/hermes-webui-docker-deployment-plan.md` for the deployment plan.

## Verification

After applying the configuration and restarting Traefik, the following checks passed:

1. Traefik logs showed no errors related to the new routers.
2. `curl -I https://web.hermes.dev.aldof.duckdns.org` returned HTTP 200 (after following redirects).
3. The response body contained the Hermes login page HTML.
4. From Traefik container: `docker exec traefik wget -qO- http://hermes-webui:8787/health` returns `{"status":"ok"}`

## Files modified

- Template: `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml`
- Runtime: `~/dev/04-network-traefik/routes.yml` (copied from template)

## Related commands

```bash
# Apply via Ansible (recommended)
cd ~/dev/01-core-infra
./install.sh

# Or manually copy and restart
cp ~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml ~/dev/04-network-traefik/routes.yml
cd ~/dev/04-network-traefik
docker compose restart traefik
```
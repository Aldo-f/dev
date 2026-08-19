---
name: freellmapi-integration
description: Deploy freellmapi via Ansible using Docker and Traefik.
trigger: User requests to deploy freellmapi using Ansible with Docker and Traefik, or debug HTTPS 404 on freellm.aldof.duckdns.org.
agents: hermes-agent
---

## Overview
This skill automates the deployment of the freellmapi service using Ansible, ensuring Docker is installed, user permissions are set, and Traefik routing is configured for access via a custom domain.

## Critical Architecture: Two docker-compose.yml Files

**The freellmapi repo has TWO relevant docker-compose.yml files from different git repos:**

| Location | Repo | Purpose |
|---|---|---|
| `~/dev/02-ai-freellm/docker-compose.yml` | `aldo-f/freellmapi` (branch `upstream`) | **Runtime** — Docker Compose reads this one at `docker compose up -d` |
| `~/dev/01-core-infra/templates/infra/02-ai-freellmapi/infra/docker-compose.yml` | `aldo-f/01-core-infra` (branch `main`) | **Template** — deployed to `~/dev/02-ai-freellm/infra/` by Ansible |

⚠️ **These are different files.** The root `docker-compose.yml` is NOT overwritten by Ansible — only `infra/docker-compose.yml` is. After a `git pull` on the freellmapi repo, the root docker-compose.yml resets to upstream, and any manual additions (like `traefik_net`) are lost. Always push fixes to BOTH repos.

## Steps
1. **Ensure Ansible is available** (assumed present in environment).
2. **Run the Ansible playbook** at `~/dev/01-core-infra/ansible/playbooks/site.yml`. It handles:
   - Docker install, user in docker group, Docker service started
   - Clones freellmapi repo (branch `upstream`) into `~/dev/02-ai-freellm`
   - Installs Node.js deps, builds, deploys via Docker Compose
3. **Configure Traefik routing** — edit BOTH files (see Pitfalls: Runtime/template divergence):
   - **Template**: `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml`
   - **Runtime**: `~/dev/04-network-traefik/routes.yml`
   - Routes file must use proper Traefik v3 `http:` format with three sections:
     * **Routers**: one HTTP router (entryPoint `web`) with `https-redirect` middleware, one HTTPS router (entryPoint `websecure`) with TLS using `certResolver: myresolver`
     * **Services**: loadBalancer → `http://freellmapi:3001`
     * **Middlewares**: redirectScheme to https, permanent
   - **Critical: ensure freellmapi docker-compose declares `traefik_net`** in BOTH locations — the runtime root (`~/dev/02-ai-freellm/docker-compose.yml`) and the template (`~/dev/01-core-infra/templates/infra/02-ai-freellmapi/infra/docker-compose.yml`). Each needs:
     * `networks: traefik_net` on the freellmapi service
     * Top-level `networks: { traefik_net: { external: true } }`
   - Ensure Traefik static config has file provider → `/etc/traefik/routes.yml`
   - Ensure external volume `04-network-traefik_letsencrypt` exists
4. **Commit BOTH repos** after any fix — see "Commit workflow" below.
5. **Confirm** — `https://freellm.aldof.duckdns.org/` returns 200 (freellmapi dashboard).

## Diagnosing "Traefik 404 After Reboot"

When `https://freellm.aldof.duckdns.org/` returns 404 but `http://192.168.0.5:3001/` works, run these three checks:

```bash
# 1. Is freellmapi on traefik_net?
docker inspect 02-ai-freellm-freellmapi-1 --format '{{json .NetworkSettings.Networks}}'
# Expected: "traefik_net" only. If it shows "02-ai-freellm_default" etc., fix docker-compose.yml.

# 2. Does routes.yml use Traefik v3 format?
cat ~/dev/04-network-traefik/routes.yml
# Must start with "http:" and have routers/services/middlewares sections.
# Old top-level "routes:" format is silently ignored by Traefik v3 → 404.

# 3. Does routes.yml cover websecure (HTTPS)?
# Must have a router with entryPoints: ["websecure"] and a tls: block.
# Without these, HTTPS traffic hits Traefik with no matching route → 404.
```

**Root cause is usually one or more of these.** Fix both template and runtime, then:

```bash
# Recreate freellmapi on the right network
docker compose -f ~/dev/02-ai-freellm/docker-compose.yml up -d

# Recreate Traefik (down+up, NOT restart — avoids stale socket binding)
docker compose -f ~/dev/04-network-traefik/docker-compose.yml down
docker compose -f ~/dev/04-network-traefik/docker-compose.yml up -d

# Verify
curl -k -H "Host: freellm.aldof.duckdns.org" https://localhost:443/ | head -3
# Should return freellmapi dashboard HTML (200)
```

## Commit Workflow

After fixing any runtime issue, Push to BOTH repos:

1. **01-core-infra** — edit template, then commit+push:
   ```bash
   cd ~/dev/01-core-infra
   git add templates/infra/04-network-traefik/routes.yml
   git commit -m "fix: ..."
   git push origin main
   ```
2. **freellmapi repo** — if root docker-compose.yml was fixed:
   ```bash
   cd ~/dev/02-ai-freellm
   # Ensure remote uses SSH (HTTPS won't auth in headless sessions)
   git remote set-url origin git@github.com:Aldo-f/freellmapi.git
   git add docker-compose.yml
   git commit -m "fix: connect freellmapi to traefik_net"
   git push origin upstream
   ```

## Pitfalls
- **Runtime/template divergence**: The template at `templates/infra/02-ai-freellmapi/infra/docker-compose.yml` may already have correct `traefik_net` config, but the runtime at `~/dev/02-ai-freellm/docker-compose.yml` can fall behind during manual edits or a reboot. Always check both — the runtime file is the one Docker uses. A mismatch after reboot is a classic symptom: container is up, Traefik is up, but HTTPS returns 404 because the container is on the wrong network.
- **Traefik restart loop**: If Traefik gets stuck in a restart loop (port binding errors), `docker compose restart` may not break the cycle. Use `docker compose down` followed by `docker compose up -d` to fully recreate the container and release stale socket references.
- **Docker DNS resolution failure**: Even with containers on the same network, Traefik's file provider sometimes cannot resolve container hostnames via Docker's internal DNS. Fallback: use the host IP in the service URL (e.g., `http://192.168.0.5:3001`) instead of the container name. This is more reliable than relying on Docker DNS for the Traefik file provider.
- **Target service binding to localhost only**: The freellmapi container defaults to binding on `127.0.0.1` (localhost only), making it unreachable from Traefik on a different container. Set `HOST_BIND=0.0.0.0` in the docker-compose environment or `.env` file so the service listens on all interfaces. Without this, Traefik gets connection refused even though the container is healthy.
- **Service URL must use Docker DNS**: Use `http://freellmapi:3001` in the service URL, not the host IP. Docker's internal DNS resolves container names on the same network, and Traefik routes to the container name, not the host bridge. Using the host IP (`http://192.168.0.5:3001`) may work when the container also publishes that port, but Docker DNS is more reliable and survives IP changes.
- **Finding the API key**: When you need the freellmapi unified API key, check the first ~20 lines of its docker logs (`docker logs 02-ai-freellm-freellmapi-1 2>&1 | head -20`). It prints `Your unified API key: freellmapi-...` on every startup. Do not search config files or env files for it — it's an auto-generated runtime key.
- **Ansible module availability**: The playbook originally used `community.docker.docker_network`, which may not be installed. Use a simple `docker network create` command with `ignore_errors: true` instead to avoid failures on existing networks.
- **Absolute script_dir**: Ensure `script_dir` is set to the absolute repository path (`/home/aldo/dev/01-core-infra`). Using a relative workdir caused template lookups to fail.
- **HTTPS push to freellmapi fails**: The freellmapi repo remote may be HTTPS which requires interactive auth. Switch to SSH with `git remote set-url origin git@github.com:Aldo-f/freellmapi.git` in headless/automated sessions.
- **Git safe.directory**: When cloning repos into owned directories, ensure the directory is marked safe (`git config --global --add safe.directory <path>`).
- **Docker socket permissions**: If the user is not in the `docker` group or the Docker daemon is not running, the deployment will fail.
- **Traefik dynamic config**: Traefik v3 expects a full `http:` section with routers, middlewares, and services. The simplified flat format (`routes:/services:`) will be silently ignored. Use the full YAML as documented in `references/traefik-routes-for-freellmapi.md`.
- **Docker volume permissions**: The LetsEncrypt volume must exist before starting Traefik. Create it with `docker volume create 04-network-traefik_letsencrypt` if missing.
- **ENCRYPTION_KEY must match stored keys**: If the freellmapi container is recreated with a new `ENCRYPTION_KEY` (or auto-generates one), all previously stored provider API keys become unreadable (`decrypt-error` in logs). The vault (`freellmapi-credentials.yml`) only stores the encryption key and basic config — **it does NOT store provider API keys**. Provider keys must be re-entered via the freellmapi web UI (`http://<host>:3001`) after any key change.
- **Health check for decrypt errors**: After restart, run `docker logs 02-ai-freellm-freellmapi-1 2>&1 | grep "decrypt-error"` — count should be 0. Non-zero means stored keys need re-entry.
- **Container must use correct ENCRYPTION_KEY**: Verify with `docker inspect 02-ai-freellm-freellmapi-1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep ENCRYPTION_KEY` — must match the vault value (`4ba635a9...`). If it shows a different key (e.g. `bc738c...`), the `.env` was not rendered correctly or a stale `.encryption-key` file exists in the Docker volume.
- **Clean stale encryption key file**: Before recreating container after fixing `.env`, delete both `/home/aldo/dev/02-ai-freellm/.encryption-key` and `/var/lib/docker/volumes/02-ai-freellm_freellmapi-data/_data/.encryption-key` (sudo) so the container uses the `.env` value instead of auto-generating.

## References
- See `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml` for the Traefik route definition.
- See `~/dev/02-ai-freellm/docker-compose.yml` for the freellmapi service definition (managed by the Ansible playbook).
- See `references/traefik-routes-for-freellmapi.md` for detailed guidance on configuring Traefik v3 dynamic routes for freellmapi with HTTP-to-HTTPS redirect and Let's Encrypt TLS.
- See `references/docusaurus-deployment-fix.md` for detailed notes on debugging and fixing the 01-core-infra Docusaurus documentation site deployment.
- See `references/deployment-session-2026-07-28.md` for prior deployment session details.
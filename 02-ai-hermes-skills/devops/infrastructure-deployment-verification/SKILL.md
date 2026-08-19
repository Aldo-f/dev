---
name: infrastructure-deployment-verification
category: devops
description: Verify infra deployments safely without manual checks.
---

# Infrastructure Deployment Verification

Use when verifying automated infrastructure deployments complete successfully without manual inspection.

## Quick Validation Pattern

```bash
# 1. Check containers are running
docker ps --format "table {{.Names}}\t{{.Status}}"

# 2. Verify network placement (traefik_net, docker_bridge, etc.)
docker inspect --format='{{json .NetworkSettings.Networks}}' <container>

# 3. Check routes/config files
grep -E "host1|host2" /path/to/config.yml

# 4. Verify health checks
docker inspect --format='{{.State.Health}}' <container>

# 5. Test endpoints
curl -s -o /dev/null -w "%{http_code}" http://service.domain:PORT
```

## Three-Layer Verification Stack (Established Pattern)

For production-grade verification, run all three layers against real runtime:

### Layer 1: Python Verification Script (`tests/verify_deployment.py`)
```python
# Verifies: container running, network attachment, routes file content, health status
python3 tests/verify_deployment.py
# ✓ Plex container running
# ✓ Plex on traefik_net
# ✓ Qbittorrent container running
# ✓ Qbittorrent on traefik_net
# ✓ Nextcloud container running
# ✓ Nextcloud on traefik_net
# ✓ Traefik routes contains plex.aldof.duckdns.org
# ✓ Traefik routes contains qbittorrent.aldof.duckdns.org
# ✓ Nextcloud container healthy
```

### Layer 2: Ansible Playbook (`tests/verify.yml`)
```yaml
- hosts: localhost
  connection: local
  vars:
    docker_inspect_format: "{{ '{{' }}json .NetworkSettings.Networks{{ '}}' }}"
    docker_inspect_health: "{{ '{{' }}json .State.Health{{ '}}' }}"
  tasks:
    - shell: "docker inspect plex --format='{{ docker_inspect_format }}'"
      register: plex_net
    - assert: { that: ["'traefik_net' in plex_net.stdout"] }
    # ... routes file content, health checks
```
Run: `ansible-playbook -i "localhost," tests/verify.yml`

### Layer 3: Template Structure Validation
```bash
# Ad-hoc script validates:
# - networks: ['traefik_net'] present
# - healthcheck section present
# - no network_mode: host
# - restart policy defined
# - ${VAR} placeholders for secrets
python3 -c "
import yaml
for f in ['plex','qbittorrent','nextcloud']:
    with open(f'templates/infra/05-media-{f}/docker-compose.yml') as fp:
        data = yaml.safe_load(fp)
    # check structure...
"
```

## Common Verification Points

### Docker Compose Healthcheck Guidelines

- **Always define a healthcheck** for services that expose a port. A typical healthcheck attempts a TCP connection or HTTP request to the service endpoint and returns success when the command exits 0.
- **Example (homepage service):**
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-fsS", "-m", "5", "http://127.0.0.1:3000"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 5s
  ```
- **Why:** Without a healthcheck, `docker inspect` will report `null` and the verification scripts may misinterpret the status. A defined healthcheck also ensures the container is fully ready before dependent services start.
- **Container name conflicts:** If `docker compose up` fails with `Conflict. The container name "/<name>" is already in use`, remove the existing container (`docker rm -f <name>`) or rename the service before redeploying.

This guidance complements the existing verification steps and helps avoid common deployment pitfalls.


### Docker Compose Deployments

```yaml
# Essential checks in templates:
- network_mode: host  # Often forbidden - use traefik_net instead
- restart policy       # Should be 'unless-stopped' or 'always'
- volume paths         # Check for correct mount points
- environment vars     # Verify ${VAR} placeholders for secrets
- healthcheck section (external domain URL, e.g., https://freellm.aldof.duckdns.org/health)  # Optional but recommended
```

### Traefik Reverse Proxy

**CRITICAL**: Do NOT use Ansible `lineinfile` with regex matching router key prefixes against routes.yml.

```yaml
# WRONG - matches BOTH 'homepage-http:' and 'homepage:'
regexp: '^    homepage'

# CORRECT - match exact node path
regexp: '^  homepage-http:|^  homepage:'
```

Better yet: copy the whole file, never edit line-by-line.

### Docker Compose Healthcheck Configuration

When adding or modifying healthchecks in docker-compose.yml:

1. **Use external URLs for healthchecks in multi-container setups**: Traefik-routed services need healthchecks that validate the full path (e.g., `https://freellm.aldof.duckdns.org/health`), not just localhost:port. Internal healthchecks can return false positives when the service is isolated from its route.

2. **Healthcheck test command must match the actual endpoint**: A common error is checking `http://localhost:3001/health` when the service doesn't actually expose a `/health` path at that URL (e.g., it serves a frontend app at `/` instead).
   
   **Lesson (08/2026)**: The FreelLM API serves a SPA frontend at `/` and `/health`, but provides a proper unauthenticated liveness probe at `/api/ping` that returns JSON `{"status":"ok","timestamp":"..."}`. Always probe the actual API endpoint, not the SPA route. Use `curl /api/ping` and validate JSON response contains `"status":"ok"`.

3. **Healthcheck resilience**: Add explicit timeouts and retries to handle transient failures:
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-fsS", "-m", "10", "https://freellm.aldof.duckdns.org/health"]
     interval: 30s
     timeout: 10s
     retries: 5
     start_period: 30s
   ```

4. **Container naming consistency**: `docker-compose ps -q` returns container IDs, NOT container names or service names. Verification scripts must use Docker labels to resolve actual container names:
   ```bash
   # WRONG: returns container IDs
   RUNNING_SERVICES=$(docker-compose -f ... ps -q)
   
   # CORRECT: resolve names via Docker label filter
   RUNNING_NAMES=$(docker ps --filter "label=com.docker.compose.project=04-network-traefik" --format '{{.Names}}')
   ```

5. **Service renaming in Traefik routes**: When renaming a service (e.g., `taskqueue` → `hermes-tq`), update both:
   - `docker-compose.yml`: service name AND `container_name` must match
   - `routes.yml`: service reference AND upstream URL must use Docker DNS name (`http://hermes-tq:8788` not `http://192.168.0.5:8788`)
   - Old domain routes must be fully removed (both HTTP and HTTPS routers + service definition)

### Flask/Dashboard Apps

When Flask renders HTML templates, verify:

1. Template files exist at deploy target
2. Flask can read routes from www-data-protected paths
3. Metrics endpoints return valid JSON
4. Subsite count parsing doesn't break on route format changes

## Pitfalls

| Symptom | Root Cause | Fix |
|---|---|---|
| Container running but services not accessible | Not on correct network | Check `NetworkSettings.Networks` |
| 502 Bad Gateway | Backend service down | Verify container status and dependencies |
| Health check fails with null | No healthcheck in compose | Add `healthcheck:` section |
| Traefik 504 on all routes | lineinfile corrupted routes.yml | Copy entire file, restart traefik |

## Scripts

- `verify_deployment.py` — Python script to verify container health, networks, and routes
- `verify.yml` — Ansible playbook with connection: local for infrastructure assertions
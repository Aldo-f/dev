# Hermes TQ: Compose-Level Deploy via 04-network-traefik

**Pattern**: Some services (like `hermes-tq`) are deployed directly in `04-network-traefik/docker-compose.yml` rather than via Ansible templates in `01-core-infra/templates/infra/`. This is valid for services that live in sibling repos and don't need Ansible-managed runtime dirs.

## Key Differences from Ansible-Managed Services

| Aspect | Ansible-Managed (e.g., 07-security-vaultwarden) | Compose-Level (e.g., 02-ai-hermes-tq) |
|--------|--------------------------------------------------|----------------------------------------|
| Template location | `01-core-infra/templates/infra/<service>/docker-compose.yml` | Direct in `04-network-traefik/docker-compose.yml` |
| Runtime dir | Copied to `~/dev/01-core-infra/<service>/` by Ansible | N/A - lives in `04-network-traefik` |
| Deploy trigger | `./install.sh` from 01-core-infra | `cd ~/dev/04-network-traefik && docker compose up -d --build` |
| Traefik routes | Managed in `01-core-infra/templates/infra/04-network-traefik/routes.yml` | Same routes.yml (single source) |
| Networks | Added via Ansible container role | Explicit in compose: `traefik_net` + `docker-stack_core-network` |

## Hermes TQ Specifics

**Service definition in 04-network-traefik/docker-compose.yml:**
```yaml
hermes-tq:
  build:
    context: ../02-ai-hermes-tq
    dockerfile: Dockerfile
  container_name: hermes-tq
  restart: unless-stopped
  expose:
    - "8788"
  networks:
    - traefik_net
    - docker-stack_core-network
  environment:
    - HERMES_MODEL_BASE_URL=http://freellmapi-dev:3001/v1
    - HERMES_MODEL_PROVIDER=custom
  volumes:
    - taskqueue-data:/app/tasks
    - /home/aldo/.hermes:/root/.hermes
    - /home/aldo/dev/02-ai-hermes-skills:/home/aldo/dev/02-ai-hermes-skills:ro
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8788/api/stats"]
    interval: 30s
    timeout: 10s
    retries: 5
```

**Traefik route (in routes.yml):**
```yaml
hermes-tq-http:
  rule: "Host(`tq.hermes.dev.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
    - ipAllowList
  service: hermes-tq
hermes-tq:
  rule: "Host(`tq.hermes.dev.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  service: hermes-tq
  tls:
    certResolver: myresolver
  middlewares:
    - ipAllowList

# Service definition
hermes-tq:
  loadBalancer:
    servers:
      - url: "http://hermes-tq:8788"
```

## Verification Commands

```bash
# Check container health
docker ps --filter "name=hermes-tq" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Healthcheck output
docker inspect hermes-tq --format '{{json .State.Health}}' | python3 -m json.tool

# API via Traefik (HTTPS, with IP allowlist)
curl -sf https://tq.hermes.dev.aldof.duckdns.org/api/stats

# API via Traefik container (internal)
docker exec traefik wget -qO- http://hermes-tq:8788/api/stats

# UI load test
curl -sf https://tq.hermes.dev.aldof.duckdns.org/ | head -20
```

## When to Use This Pattern

Use compose-level deployment when:
- The service is a development/auxiliary service in a sibling repo (02-ai-*, 06-apps-*)
- The service doesn't need Ansible-managed runtime dirs or .env generation
- The service is simple enough that direct compose is clearer
- You want faster iteration without full Ansible runs

Use Ansible-managed when:
- The service needs secret injection, .env templating, or host path management
- The service is part of core infrastructure (01-core, 04-network, 07-security)
- Multiple hosts or complex orchestration is needed
- Consistency with existing Ansible patterns is required
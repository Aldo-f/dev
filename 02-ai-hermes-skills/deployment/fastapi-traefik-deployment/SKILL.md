---
name: fastapi-traefik-deployment
description: Deploy FastAPI behind Traefik using Docker Compose.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [fastapi, traefik, docker, deployment]
    related_skills: []
---

# FastAPI‑Traefik Deployment

## When to use
- You have a FastAPI service you want to expose publicly via HTTPS.
- Traefik is already running as a reverse proxy (Docker‑Compose based).
- You prefer the service to be containerised so Traefik can reach it on the Docker network.

## Core steps
1. **Create a Dockerfile** in the FastAPI project root:
```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt
EXPOSE 8788
CMD ["/app/.venv/bin/uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8788"]
```
2. **Add a service** to your `docker‑compose.yml` (same directory as `traefik.yml`):
```yaml
services:
  taskqueue:
    build:
      context: ../02-ai-taskqueue
      dockerfile: Dockerfile
    restart: unless-stopped
    expose:
      - "8788"
    networks:
      - traefik_net
```
3. **Update Traefik `routes.yml`** to point to the container:
```yaml
taskqueue:
  loadBalancer:
    servers:
      - url: "http://taskqueue:8788"
```
4. **Re‑build and restart** the stack:
```bash
cd /path/to/04-network-traefik
docker-compose up -d --build
```
5. **Test** the endpoint:
```bash
curl -I https://taskqueue.aldof.duckdns.org   # should return 200 OK
curl -s https://taskqueue.aldof.duckdns.org/api/tasks | python -m json.tool
```

## Common pitfalls & fixes
- **Wrong URL in `routes.yml`.** Use the service name (`taskqueue`), not a host‑machine IP.
- **Port not exposed.** Forgetting `expose: - "8788"` makes Traefik unable to reach the container.
- **Binding to localhost.** `uvicorn` must listen on `0.0.0.0`; binding to `127.0.0.1` isolates it from Docker.
- **Stale images.** After Dockerfile changes, always run `docker-compose up -d --build`.
- **Network mismatch.** The service must join the same network (`traefik_net`) that Traefik uses.

## References
- `references/Dockerfile.example.md` – full Dockerfile with comments.
- `references/docker-compose-snippet.md` – minimal compose snippet to copy‑paste.
- `references/routes.yml-entry.md` – correct Traefik router/service entry.

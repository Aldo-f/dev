---
name: hermes-taskqueue
description: Deploy Hermes task queue with Docker, FastAPI, and Traefik.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, docker, task-queue, deployment, fastapi, traefik]
    related_skills: [docker-volume-persistence, fastapi-traefik-deployment, hermes-agent]
---

# Hermes Task Queue

Deploy a persistent, web-accessible task queue where tasks are markdown files executed headlessly via `hermes -z "<markdown>"`.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Browser   │────▶│  Traefik :443   │────▶│  FastAPI :8788  │
│  Web UI         │     │  HTTPS          │     │  (Docker)       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────────┐
                                                  │  Worker Loop    │
                                                  │  (same container)│
                                                  │  hermes -z <task>│
                                                  └────────┬────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  Task Storage   │
                                                  │  Docker volume  │
                                                  │  /app/tasks/    │
                                                  └─────────────────┘
```

## Quick Deploy

### 1. Create Project Structure

```bash
mkdir -p ~/dev/02-ai-taskqueue
cd ~/dev/02-ai-taskqueue

# Create essential files
cat > requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn==0.30.6
EOF

cat > Dockerfile << 'EOF'
FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl python3-venv && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --break-system-packages hermes-agent
RUN pip install --break-system-packages -r requirements.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
EOF

cat > entrypoint.sh << 'EOF'
#!/bin/bash
python worker.py &
exec uvicorn server:app --host 0.0.0.0 --port 8788
EOF

chmod +x entrypoint.sh
```

### 2. Docker Compose Configuration

In your Traefik `docker-compose.yml`:

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
    volumes:
      - taskqueue-data:/app/tasks
      - /home/aldo/.hermes:/root/.hermes    # Read-write! Hermes writes logs here
      - /home/aldo/dev/02-ai-hermes-skills:/home/aldo/dev/02-ai-hermes-skills:ro

volumes:
  taskqueue-data:
```

**Critical**: Mount `~/.hermes` **read-write** (not `:ro`) — Hermes needs to write to `~/.hermes/logs/` and other runtime files.

### 3. Traefik Route

In `routes.yml`:

```yaml
http:
  routers:
    taskqueue-http:
      rule: "Host(`taskqueue.aldof.duckdns.org`)"
      entryPoints:
        - web
      middlewares:
        - https-redirect
      service: taskqueue
    taskqueue:
      rule: "Host(`taskqueue.aldof.duckdns.org`)"
      entryPoints:
        - websecure
      service: taskqueue
      tls:
        certResolver: myresolver
  services:
    taskqueue:
      loadBalancer:
        servers:
          - url: "http://taskqueue:8788"   # Use container name, not IP
```

### 4. Deploy

```bash
cd ~/dev/04-network-traefik
docker-compose up -d --build
```

## Task Format

Tasks are markdown files with a `### VALIDATION` section:

```markdown
# Task Title

[Instructions for Hermes to execute]

### VALIDATION
- [ ] Check item 1
- [ ] Check item 2
```

The worker:
1. Runs `hermes -z "<task.md content>"`
2. Captures stdout/stderr to `run-<timestamp>.log`
3. Parses the `### VALIDATION` checkboxes
4. If exit=0 AND all checkboxes checked → status `done`
5. Otherwise → status `needs_fix`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Create task (JSON: `{markdown, start_at, priority}`) |
| GET | `/api/tasks/{id}` | Get task details + markdown |
| PATCH | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| POST | `/api/tasks/{id}/run` | Force-run immediately |

## Debugging

See `references/docker-pitfalls.md` for common issues and fixes.

## Files Created

- `~/dev/02-ai-taskqueue/` — Project root
- `~/dev/04-network-traefik/docker-compose.yml` — Added taskqueue service
- `~/dev/04-network-traefik/routes.yml` — Added taskqueue routes
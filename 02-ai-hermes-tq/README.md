# Hermes TQ

A lightweight, multi-node capable task runner for **Hermes Agent**.  
Designed to run on Raspberry Pi with **Neo-Brutalist** UX and robust status tracking.

## 🚀 Features

- **Sequential execution**: Ensures only one task runs at a time (resource friendly).
- **Hermes self-delegation**: Executes tasks via `hermes -z` headless mode.
- **Smart Validation**: Parses `### VALIDATION` blocks to determine success.
- **Full CRUD**: Create, Edit, Delete, Reset, and Run tasks via Web UI or API.
- **Live Logs**: View real-time output from Hermes directly in the dashboard.
- **Scheduling**: Optional `start_at` field for future tasks.
- **Priority**: Higher priority tasks move to the front of the queue.

## 🛠 Architecture

- **Backend**: FastAPI (Python 3.13)
- **Frontend**: Vanilla JS + CSS (Neo-Brutalist design)
- **Storage**: JSON + Markdown files (persistent via Docker volumes)
- **Worker**: Background loop with filesystem locking.

## 📦 Quick Start (Docker)

The task queue is integrated into the core infra.

```bash
# Start/Update the service
cd ~/dev/04-network-traefik
docker-compose up -d --build
```

Access the UI at: **[https://taskqueue.aldof.duckdns.org](https://taskqueue.aldof.duckdns.org)**

## 📝 Task Format

Tasks are defined in **Markdown**. To enable automated validation, add a `### VALIDATION` section:

```markdown
# My Task Title
Run some commands here...

### VALIDATION
- [ ] Condition 1
- [ ] Condition 2
```

## 🔌 API Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | List all tasks |
| `/api/stats` | GET | Queue statistics |
| `/api/tasks` | POST | Create new task |
| `/api/tasks/{id}` | GET | Task details + markdown |
| `/api/tasks/{id}` | PATCH | Update task |
| `/api/tasks/{id}/run` | POST | Force immediate execution |
| `/api/tasks/{id}/reset` | POST | Reset status to queued |
| `/api/tasks/{id}/log` | GET | View execution log |

---
*Developed for Pi 5 & Pi 3B multi-node setups.*

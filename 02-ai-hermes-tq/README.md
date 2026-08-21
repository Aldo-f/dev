# Hermes Task Queue (Hermes TQ)

A lightweight task management system built with FastAPI that integrates with the Hermes AI agent ecosystem.

## Overview

Hermes TQ provides a kanban board interface for managing and executing AI-assisted tasks. Tasks are defined in markdown format and can be executed using the `hermes -z` command for headless AI processing.

## Features

- 📋 Kanban board interface for task visualization
- ⚡ Background worker for automatic task processing
- 🔄 RESTful API for task management
- 💾 Persistent task storage (JSON + Markdown)
- 🎨 Natural language task input
- 📊 Task statistics and monitoring
- 🔐 IP-restricted access via Traefik
- 🐳 Dockerized deployment

## Project Structure

```
.
├── static/                 # Frontend assets (CSS, HTML, JS)
│   ├── kanban.css         # Kanban board styling
│   ├── kanban.html        # Main kanban board interface
│   ├── dashboard.html     # Hermes subsystem dashboard
│   └── index.html         # Landing page
├── tasks/                 # Runtime task storage (not committed)
├── tests/                 # Test suite
├── server.py              # FastAPI application
├── worker.py              # Background task processor
├── executor.py            # Task execution engine (hermes -z)
├── state.py               # Task state management
├── validate.py            # Markdown validation parsing
├── entrypoint.sh          # Container startup script
├── Dockerfile             # Container build instructions
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── AGENTS.md              # Operating rules for agents
```

## Deployment

### Via Traefik (Recommended)

```bash
cd ~/dev/04-network-traefik
docker compose up -d --build
```

### Manual Docker Run

```bash
docker run -d \
  --name hermes-tq \
  -p 8788:8788 \
  -v $(pwd)/tasks:/app/tasks \
  --network traefik_net \
  --network docker-stack_core-network \
  ghcr.io/Aldo-f/02-ai-hermes-tq:latest
```

## API Endpoints

- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/run` - Execute task immediately
- `POST /api/tasks/{id}/reset` - Reset task to queued
- `GET /api/tasks/{id}/log` - Get task execution log
- `GET /api/stats` - Get task statistics
- `GET /api/subsystems` - Discover Hermes subsystems
- `GET /kanban` - Kanban board interface
- `GET /` - Landing page

## Task Format

Tasks are stored as markdown files with optional validation sections:

```markdown
# Task Title

Task description goes here.

### VALIDATION
- [ ] Checklist item 1
- [x] Completed item
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python worker.py &  # Start worker in background
uvicorn server:app --host 0.0.0.0 --port 8788  # Start API server
```

## Conventions

- Store task metadata in JSON format (`meta.json`)
- Store task content in Markdown (`task.md`)
- Store execution logs with timestamps (`run-{timestamp}.log`)
- Use filesystem locking for worker coordination
- Prioritize tasks by priority level and creation time
- Limit retry attempts to prevent infinite loops

## License

Private - For personal use only.
# Hermes Task Queue PoC Implementation

## Overview

A proof-of-concept task queue system that:
1. Stores tasks as markdown files with `### VALIDATION` sections
2. Runs tasks sequentially via `hermes -z "<markdown>"`
3. Evaluates validation results and supports retries
4. Exposes a web UI for task management
5. Serves via Traefik at `https://taskqueue.aldof.duckdns.org`

## Key Design Decisions

### Sequential Execution
- Single worker process with file-based locking (`queue.lock`)
- No parallel task execution (appropriate for Pi resources)
- Lock released during Hermes execution to allow UI edits

### Validation Pattern
- Tasks include `### VALIDATION` section with checkboxes
- Parser handles `- [ ]`, `- [x]`, `1. [ ]`, `* [ ]` formats
- Success requires: exit_code=0 AND all checks marked `[x]`

### Storage
- Tasks stored in `tasks/<uuid>/` directories
- Each task has: `task.md`, `meta.json`, `run-<timestamp>.log`
- Git-ignored runtime data, version-controlled code

## Technical Implementation

### Dockerfile (Production)
```dockerfile
FROM python:3.13-slim
RUN apt-get update && apt-get install -y curl python3-venv
WORKDIR /app
COPY . /app
RUN pip install --break-system-packages -r requirements.txt
EXPOSE 8788
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8788"]
```

**Note**: Using `--break-system-packages` with system Python (not venv) to avoid ensurepip issues in Docker.

### Worker Pattern
```python
def main_loop():
    while True:
        try:
            # acquire lock
            fd = os.open('queue.lock', os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX)
            
            task = pick_next_task()  # filter ripe tasks
            if not task:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
                time.sleep(5)
                continue
                
            # mark running, release lock
            save_meta(task['id'], status='running')
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            
            # execute
            exec_res = run_hermes(task['id'])
            
            # re-acquire to update
            fd = os.open('queue.lock', os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX)
            evaluate_task(task['id'], exec_res)
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            
        except Exception as e:
            print('Worker error:', e)
            time.sleep(5)
```

### Traefik Integration
- Container name: `taskqueue` (automatically resolvable via Docker DNS)
- Network: `traefik_net` (shared with Traefik container)
- URL in routes.yml: `http://taskqueue:8788` (not IP-based)

## Lessons Learned

1. **Docker network access**: Service must be on same network as Traefik (`traefik_net`)
2. **Container DNS**: Use service name (`taskqueue`) not IP for reliability
3. **Port binding**: Service must bind to `0.0.0.0` not `127.0.0.1`
4. **Python venv in Docker**: System pip with `--break-system-packages` works better than venv in slim images
5. **Lock granularity**: Release lock during long-running tasks to allow UI edits

## Files Created

- `/home/aldo/dev/02-ai-taskqueue/` - Complete PoC implementation
- `/home/aldo/dev/04-network-traefik/routes.yml` - Added taskqueue route
- `/home/aldo/dev/04-network-traefik/docker-compose.yml` - Added taskqueue service
- `/home/aldo/.hermes/plans/2026-08-02_taskqueue-poc.md` - Original plan document

## Status

✅ Fully operational at https://taskqueue.aldof.duckdns.org
✅ REST API functional (`/api/tasks`, `/api/tasks/{id}`)
✅ Worker processing tasks via Hermes
✅ Docker containerized with Traefik routing

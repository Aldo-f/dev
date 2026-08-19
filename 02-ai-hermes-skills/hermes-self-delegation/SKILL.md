---
name: hermes-self-delegation
description: Headless Hermes task runner with validation via `hermes -z`
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Self‑Delegation Skill

Run Hermes Agent headlessly from a script or worker loop using `hermes -z "<markdown>"`.  
This pattern is useful for executing a series of tasks defined in markdown files,  
each with an optional `### VALIDATION` section that the automation can check  
to determine success and trigger retries.

## When to use

- You have a queue of tasks stored as markdown (one file per task).  
- Each task may contain a validation checklist (checkboxes) that can be  
  inspected after execution.  
- You want a single‑worker, sequential execution model (e.g. on a Raspberry Pi).  
- You need automatic retries based on validation results.

## How it works

1. **Read the markdown file** – the full content becomes the prompt for Hermes.  
2. **Execute headlessly** – run `hermes -z "<markdown>"` (nointeractive voice_recognition: true)` we intend to provide a full paraphrasing of the above in a clearer, more polished tone. Below is the revised version of the passage, with improved grammar, flow, and clarity while preserving the original meaning:

---

3. **Parse validation** – extract the `### VALIDATION` block (or `## VALIDATION`)  
   and treat each line that starts with `- [ ]` or `- [x]` as a checklist item.  
4. **Decide outcome** – the task succeeds if:  
   - Hermes exit code is `0` **and**  
   - every validation item is checked (`[x]`).  
5. **Retry logic** – on failure, increment a retry counter and, if under the  
   configured maximum, re‑queue the task (optionally with the previous log  
   attached as context).  
6. **Locking** – use a simple file‑based lock (e.g. `queue.lock`) to guarantee  
   that only one Hermes invocation runs at a time.

## Step‑by‑step example (bash‑like pseudocode)

```bash
LOCK=queue.lock
TASK_DIR=tasks

while true; do
    # acquire exclusive lock
    exec 200>$LOCK
    flock -x 200
    # pick next ripe task (priority, start_at, etc.)
    TASK_ID=$(pick_next_task)   # your own logic
    if [ -z "$TASK_ID" ]; then
        flock -u 200
        exec 200<&-
        sleep 5
        continue
    fi
    # mark running
    update_meta $TASK_ID status=running
    flock -u 200
    exec 200<&-

    # run Hermes
    MD=$(cat "$TASK_DIR/$TASK_ID/task.md")
    LOG="$TASK_DIR/$TASK_ID/run-$(date -u +%Y%m%dT%H%M%SZ).log"
    START=$(date +%s.%N)
    hermes -z "$MD" >"$LOG" 2>&1
    EXIT=$?
    END=$(date +%s.%N)

    # update meta with timing/exit/log
    update_meta $TASK_ID \
        exit_code=$EXIT \
        log_path=$LOG \
        start_ts=$START \
        end_ts=$END

    # parse validation
    CHECKS=$(parse_validation "$MD")   # returns 0 if all checked
    if [ $EXIT -eq 0 ] && [ $CHECKS -eq 0 ]; then
        update_meta $TASK_ID status=done
    else
        update_meta $TASK_ID status=needs_fix
        # optional: create follow‑up task with log as context
    fi
done
```

## Pitfalls & troubleshooting

- **Exit code vs. output** – some Hermes commands may print useful info to stdout  
  even on non‑zero exit; always check both the exit code and the validation.  
- **Validation parsing** – be tolerant of different list markers (`*`, `1.`) and  
  whitespace; a simple regex like `\s*[-*]\s*\[[ xX]\]` works for most cases.  
- **Locking on NFS** – if your task directory is on a network filesystem, use  
  a lock library that supports it (e.g. `flock` may fail). Consider a lock file  
  on a local tmpfs.  
- **Hermes startup time** – the first `hermes -z` may take a few seconds to  
  load plugins; factor this into your loop’s sleep interval.  
- **Log rotation** – prune old run logs periodically to avoid disk‑filling.

## Implementation example (Python FastAPI + Worker)

The PoC implementation at `~/dev/02-ai-taskqueue/` demonstrates this pattern:

### Project structure
```
02-ai-taskqueue/
├── server.py          # FastAPI server (CRUD + UI)
├── worker.py          # Background worker (Hermes delegation)
├── state.py           # Task CRUD operations
├── executor.py        # `hermes -z` wrapper
├── validate.py        # Markdown VALIDATION parser
├── tasks/             # Runtime task storage
└── static/index.html  # Dashboard UI
```

### Key patterns used

1. **Single-worker with file lock**:
```python
import fcntl
lock_path = 'queue.lock'
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
fcntl.flock(fd, fcntl.LOCK_EX)  # acquire
# ... run task ...
fcntl.flock(fd, fcntl.LOCK_UN)  # release
os.close(fd)
```

2. **Hermes execution wrapper**:
```python
import subprocess, shlex
cmd = f"hermes -z {shlex.quote(prompt)}"
proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
```

3. **Validation parsing**:
```python
# Parse markdown validation section
def parse_validation_section(md: str) -> list[dict]:
    """Extract validation items from markdown."""
    validation = []
    in_section = False
    for line in md.splitlines():
        if re.match(r"^#{1,6}\s+VALIDATION", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^#", line):
            break
        m = re.search(r"\[([ xX])\]", line)
        if m:
            checked = m.group(1).lower() == 'x'
            text = re.sub(r"^\s*[-*\d.]+\s*\[.[\]\]\s*", "", line).strip()
            validation.append({'checked': checked, 'text': text})
    return validation
```

### Docker deployment

The PoC uses Docker for Traefik integration:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --break-system-packages -r requirements.txt
EXPOSE 8788
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8788"]
```

### Public access via Traefik

Add to `routes.yml`:
```yaml
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
        - url: "http://taskqueue:8788"
```
import json, os, time, uuid

def _meta_path(task_id: str) -> str:
    return os.path.join('tasks', task_id, 'meta.json')

def make_task(md: str, start_at: str | None = None, priority: int = 0) -> str:
    """Create a new task directory with given markdown content.
    Returns the generated task_id (UUID)."""
    task_id = uuid.uuid4().hex
    task_dir = os.path.join('tasks', task_id)
    os.makedirs(task_dir, exist_ok=True)
    # write markdown
    with open(os.path.join(task_dir, 'task.md'), 'w') as f:
        f.write(md)
    meta = {
        'id': task_id,
        'status': 'queued',
        'created_at': time.time(),
        'priority': priority,
        'retries': 0,
        'max_retries': 2,
        'start_at': start_at,
    }
    with open(_meta_path(task_id), 'w') as f:
        json.dump(meta, f)
    return task_id

def load_meta(task_id: str) -> dict:
    path = _meta_path(task_id)
    with open(path) as f:
        return json.load(f)

def save_meta(task_id: str, **updates) -> None:
    meta = load_meta(task_id)
    meta.update(updates)
    with open(_meta_path(task_id), 'w') as f:
        json.dump(meta, f)

def list_tasks() -> list[dict]:
    base = 'tasks'
    if not os.path.isdir(base):
        return []
    tasks = []
    for task_id in os.listdir(base):
        try:
            meta = load_meta(task_id)
            tasks.append(meta)
        except Exception:
            continue
    return tasks

def is_ripe(task_id: str) -> bool:
    meta = load_meta(task_id)
    if meta.get('status') != 'queued':
        return False
    start = meta.get('start_at')
    if not start:
        return True
    # ISO timestamp or epoch string; try float first
    try:
        ts = float(start)
    except ValueError:
        try:
            ts = time.mktime(time.strptime(start, "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            return False
    return time.time() >= ts

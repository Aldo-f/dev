import json, os, time, uuid

TASKS_ROOT = os.path.join(os.getcwd(), 'tasks')
os.makedirs(TASKS_ROOT, exist_ok=True)

def _meta_path(task_id: str) -> str:
    return os.path.join(TASKS_ROOT, task_id, 'meta.json')

def make_task(md: str, start_at: str | None = None, priority: int = 0) -> str:
    task_id = uuid.uuid4().hex[:12]
    task_dir = os.path.join(TASKS_ROOT, task_id)
    os.makedirs(task_dir, exist_ok=True)
    with open(os.path.join(task_dir, 'task.md'), 'w') as f:
        f.write(md)
    meta = {
        'id': task_id,
        'status': 'queued',
        'created_at': time.time(),
        'start_at': start_at,
        'priority': priority,
        'start_ts': None,
        'end_ts': None,
        'exit_code': None,
        'log_path': None,
    }
    with open(_meta_path(task_id), 'w') as f:
        json.dump(meta, f)
    return task_id

def list_tasks() -> list[dict]:
    tasks = []
    for task_id in os.listdir(TASKS_ROOT):
        try:
            meta = load_meta(task_id)
            tasks.append(meta)
        except Exception:
            pass
    return tasks

def load_meta(task_id: str) -> dict:
    with open(_meta_path(task_id)) as f:
        return json.load(f)

def save_meta(task_id: str, **updates) -> dict:
    meta = load_meta(task_id)
    meta.update(updates)
    with open(_meta_path(task_id), 'w') as f:
        json.dump(meta, f)
    return meta

def is_ripe(task_id: str) -> bool:
    meta = load_meta(task_id)
    if meta['status'] != 'queued':
        return False
    if meta.get('start_at'):
        try:
            if time.time() < float(meta['start_at']):
                return False
        except Exception:
            pass
    return True
import time, os, json
from pathlib import Path
from state import list_tasks, load_meta, save_meta, is_ripe
from executor import run_hermes
from validate import parse_validation_section

TASKS_ROOT = Path('tasks')


def pick_next_task():
    tasks = list_tasks()
    # filter ripe
    ripe = [t for t in tasks if is_ripe(t['id'])]
    if not ripe:
        return None
    # sort by priority (desc) then start_at (asc)
    def sort_key(t):
        # higher priority first
        prio = t.get('priority', 0)
        start = t.get('start_at') or ''
        return (-prio, start)
    ripe.sort(key=sort_key)
    return ripe[0]


def evaluate_task(task_id: str, exec_res: dict):
    # read markdown and validation
    md_path = TASKS_ROOT / task_id / 'task.md'
    if not md_path.exists():
        save_meta(task_id, status='failed', error='task.md missing')
        return 'failed', []
        
    md = md_path.read_text()
    checks = parse_validation_section(md)
    
    # If exit code is 0, mark as completed (trust Hermes executed successfully)
    # Validation checkboxes are informational, not auto-evaluated
    if exec_res['exit_code'] == 0:
        new_status = 'completed'
    else:
        new_status = 'failed'
        
    # Read the log to see if we can auto-check validation items
    log_path = TASKS_ROOT / task_id / exec_res['log_path'].split('/')[-1]
    log_content = ''
    if log_path.exists():
        log_content = log_path.read_text()
    
    # Auto-check validation items if log contains expected keywords
    if checks and new_status == 'completed':
        updated_md = md
        for check in checks:
            if not check['checked']:
                # Check if log contains keywords from validation
                check_text_lower = check['text'].lower()
                if any(kw in log_content.lower() for kw in check_text_lower.split()[:3]):
                    # Update the markdown to check this box
                    updated_md = updated_md.replace(
                        f"- [ ] {check['text']}",
                        f"- [x] {check['text']}"
                    )
                    updated_md = updated_md.replace(
                        f"* [ ] {check['text']}",
                        f"* [x] {check['text']}"
                    )
        if updated_md != md:
            md_path.write_text(updated_md)
            checks = parse_validation_section(updated_md)
        
    meta = load_meta(task_id)
    retries = meta.get('retries', 0)
    max_retries = meta.get('max_retries', 2)
    
    if new_status == 'failed' and retries < max_retries:
        save_meta(task_id, status='queued', retries=retries + 1)
        return 'queued', checks
        
    save_meta(task_id, status=new_status)
    return new_status, checks


def main_loop():
    while True:
        try:
            # acquire exclusive lock (blocking)
            lock_path = 'queue.lock'
            fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
            task = pick_next_task()
            if not task:
                # nothing to do – release lock and sleep
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
                time.sleep(5)
                continue
            task_id = task['id']
            # Mark as running
            save_meta(task_id, status='running')
            # release lock while running (so UI can edit)
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            # execute hermes
            exec_res = run_hermes(task_id)
            # re-acquire lock to update status
            fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX)
            new_status, checks = evaluate_task(task_id, exec_res)
            # unlock
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        except Exception as e:
            # log to console, continue
            print('Worker error:', e)
            time.sleep(5)

if __name__ == '__main__':
    # ensure tasks dir exists
    TASKS_ROOT.mkdir(exist_ok=True)
    main_loop()

import subprocess, os, datetime, time, shlex
from state import load_meta, save_meta, is_ripe
from validate import parse_validation_section

def run_hermes(task_id: str) -> dict:
    """Execute `hermes -z "<markdown>"` for the given task.
    Returns a dictionary with the execution result and log location.
    """
    md_path = os.path.join('tasks', task_id, 'task.md')
    with open(md_path, 'r') as f:
        prompt = f.read()
    # Timestamped log filename (UTC)
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    log_path = os.path.join('tasks', task_id, f'run-{ts}.log')
    cmd = f"hermes -z {shlex.quote(prompt)} --title \"TQ: {task_id[:8]}\""
    start_ts = time.time()
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=900)
    end_ts = time.time()
    # Write both stdout and stderr to the log file
    with open(log_path, 'w') as lf:
        lf.write(proc.stdout)
        lf.write('\n---ERR---\n')
        lf.write(proc.stderr)
    # Persist execution metadata
    save_meta(task_id,
        status='completed' if proc.returncode == 0 else 'failed',
        start_ts=start_ts,
        end_ts=end_ts,
        exit_code=proc.returncode,
        log_path=log_path)
    return {
        'exit_code': proc.returncode,
        'log_path': log_path,
        'start_ts': start_ts,
        'end_ts': end_ts,
    }

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from state import make_task, list_tasks, load_meta, save_meta, is_ripe
from executor import run_hermes
from validate import parse_validation_section

app = FastAPI()

# serve static files (frontend)
static_dir = Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=static_dir), name='static')

# serve hub dashboard (auto-discovered subsystems)
app.mount('/hub/static', StaticFiles(directory=static_dir), name='hub-static')

@app.get('/hub')
@app.head('/hub')
async def hub_root():
    return FileResponse(static_dir / 'dashboard.html')

@app.get('/api/subsystems')
async def get_subsystems():
    """Auto-discover Hermes subdomains (*.hermes.dev.aldof.duckdns.org) via Docker + Traefik labels."""
    import subprocess
    import re

    HERMES_SUFFIX = 'hermes.dev.aldof.duckdns.org'
    host_re = re.compile(r'Host\(`([^`]+)`\)')

    # Display info keyed by subdomain label (the part before .hermes.dev...)
    sub_meta = {
        'hermes':     {'name': 'Hermes Hub',     'desc': 'This dashboard',  'icon': '🏛️'},
        'web':        {'name': 'Hermes WebUI',   'desc': 'Chat & agent UI', 'icon': '🤖'},
        'tq':         {'name': 'Hermes Task Q',  'desc': 'Background jobs', 'icon': '⚙️'},
    }

    subsystems = []
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}\\t{{.Status}}\\t{{.Labels}}'],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            name = parts[0]
            status = parts[1]
            labels = parts[2] if len(parts) > 2 else ''

            # Pull every Host() rule from Traefik labels
            hosts = host_re.findall(labels)
            # Keep only hermes.dev.aldof.duckdns.org subdomains (incl. apex)
            hermes_hosts = [h for h in hosts if h == HERMES_SUFFIX or h.endswith('.' + HERMES_SUFFIX)]
            if not hermes_hosts:
                continue

            # Prefer the most-specific (longest) subdomain
            primary = max(hermes_hosts, key=len)
            sub_label = primary[:-len('.' + HERMES_SUFFIX)] if primary != HERMES_SUFFIX else 'hermes'

            meta = sub_meta.get(sub_label, {
                'name': sub_label.replace('-', ' ').title() or 'Hermes',
                'desc': 'Service',
                'icon': '📦',
            })

            healthy = 'healthy' in status.lower()
            running = 'up' in status.lower()

            subsystems.append({
                'name': meta['name'],
                'desc': meta['desc'],
                'icon': meta['icon'],
                'subdomain': sub_label,
                'container': name,
                'status': 'healthy' if healthy else ('running' if running else 'down'),
                'public_url': f'https://{primary}',
                'all_hosts': [f'https://{h}' for h in hermes_hosts],
            })

        subsystems.sort(key=lambda x: (0 if x['subdomain'] == 'hermes' else 1, x['name'].lower()))
        return {'subsystems': subsystems, 'domain': HERMES_SUFFIX}
    except Exception as e:
        return {'error': str(e), 'subsystems': [], 'domain': HERMES_SUFFIX}

@app.get('/')
@app.head('/')
async def root():
    # serve index.html from static (existing TQ UI)
    return FileResponse(static_dir / 'index.html')

@app.get('/api/tasks')
async def get_tasks():
    tasks = list_tasks()
    # Sort by priority desc, created_at desc
    tasks.sort(key=lambda x: (-x.get('priority', 0), -x.get('created_at', 0)))
    return tasks

@app.get('/api/stats')
async def get_stats():
    tasks = list_tasks()
    return {
        'total': len(tasks),
        'queued': len([t for t in tasks if t['status'] == 'queued']),
        'running': len([t for t in tasks if t['status'] == 'running']),
        'completed': len([t for t in tasks if t['status'] == 'completed']),
        'failed': len([t for t in tasks if t['status'] in ('failed', 'needs_fix')]),
    }

@app.post('/api/tasks/{task_id}/reset')
async def reset_task(task_id: str):
    try:
        save_meta(task_id, status='queued', start_ts=None, end_ts=None, exit_code=None, log_path=None)
        return {'status': 'reset'}
    except Exception:
        raise HTTPException(status_code=404, detail='task not found')

@app.post('/api/tasks')
async def create_task(request: Request):
    data = await request.json()
    md = data.get('markdown')
    if not md:
        raise HTTPException(status_code=400, detail='markdown required')
    start_at = data.get('start_at')
    priority = data.get('priority', 0)
    task_id = make_task(md, start_at=start_at, priority=priority)
    return {'id': task_id}

@app.get('/api/tasks/{task_id}')
async def get_task(task_id: str):
    try:
        meta = load_meta(task_id)
        # also read markdown
        md_path = Path('tasks') / task_id / 'task.md'
        md = md_path.read_text() if md_path.exists() else ''
        meta['markdown'] = md
        return meta
    except Exception:
        raise HTTPException(status_code=404, detail='task not found')

@app.patch('/api/tasks/{task_id}')
async def patch_task(task_id: str, request: Request):
    data = await request.json()
    meta_updates = {}
    if 'markdown' in data:
        md_path = Path('tasks') / task_id / 'task.md'
        md_path.write_text(data['markdown'])
    if 'start_at' in data:
        meta_updates['start_at'] = data['start_at']
    if 'priority' in data:
        meta_updates['priority'] = data['priority']
    if meta_updates:
        save_meta(task_id, **meta_updates)
    return {'status': 'updated'}

@app.delete('/api/tasks/{task_id}')
async def delete_task(task_id: str):
    task_dir = Path('tasks') / task_id
    if not task_dir.is_dir():
        raise HTTPException(status_code=404, detail='task not found')
    for p in task_dir.iterdir():
        p.unlink()
    task_dir.rmdir()
    return {'status': 'deleted'}

@app.get('/api/tasks/{task_id}/log')
async def get_task_log(task_id: str):
    meta = load_meta(task_id)
    log_path = meta.get('log_path')
    if not log_path:
        raise HTTPException(status_code=404, detail='No log available')
    full_path = Path('tasks') / task_id / Path(log_path).name
    if not full_path.exists():
        raise HTTPException(status_code=404, detail='Log file not found')
    return FileResponse(full_path, media_type='text/plain', filename=f'task-{task_id}.log')

@app.post('/api/tasks/{task_id}/run')
async def run_task(task_id: str):
    meta = load_meta(task_id)
    if meta.get('status') == 'running':
        raise HTTPException(status_code=400, detail='task already running')
    # Make it ripe and queued so the worker picks it up immediately
    save_meta(task_id, status='queued', start_at=None, start_ts=None, end_ts=None, exit_code=None, log_path=None)
    return {'status': 'queued_for_immediate_run'}

if __name__ == '__main__':
    # When running locally, default to 8788
    port = int(os.getenv('PORT', 8788))
    uvicorn.run(app, host='0.0.0.0', port=port)

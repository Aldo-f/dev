"""Hermes Hub – auto-discovered dashboard of *.hermes.dev.aldof.duckdns.org subdomains.

Proxies the /api/subsystems endpoint from hermes-tq, so all discovery
logic stays in one place (the agent that owns the docker CLI).
"""
import os
from pathlib import Path
import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

HERMES_TQ = os.environ.get('HERMES_TQ_URL', 'http://hermes-tq:8788')
static_dir = Path(__file__).parent / 'static'

app.mount('/static', StaticFiles(directory=static_dir), name='static')


@app.get('/')
@app.head('/')
async def root():
    return FileResponse(static_dir / 'index.html')


@app.get('/api/subsystems')
async def subsystems():
    """Proxy the discovery endpoint from hermes-tq."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f'{HERMES_TQ}/api/subsystems')
            return JSONResponse(content=r.json(), status_code=r.status_code)
    except Exception as e:
        return JSONResponse(content={'error': str(e), 'subsystems': []}, status_code=502)


@app.get('/api/health')
async def health():
    return {'status': 'healthy'}
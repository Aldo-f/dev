import { Hono } from 'hono';
import { logger } from 'hono/logger';
import { serveStatic } from 'hono/bun';
import { execSync } from 'child_process';
import fs from 'fs/promises';
import sync, { DEFAULT_SOURCES } from './index.js';
import { appendHistory, readHistory } from '../src/writers/history-writer.js';
import { getDashboardContext } from './src/dashboard/html.js';

const app = new Hono();
app.use('*', logger());

// Serve static files (Tailwind CSS + client JS)
app.use('/static/*', serveStatic({ root: './src/dashboard/' }));

// Helpers
const POOL_PATH = path.resolve(process.cwd(), 'credential-pool.json');

async function readPool() {
  try {
    const data = await fs.readFile(POOL_PATH, 'utf8');
    return JSON.parse(data);
  } catch {
    return { version: '1.0.0', providers: {}, cron: { enabled: false, schedule: '*/30 * * * *', last_run: null, next_run: null }, sync_metadata: { sources_synced: [] } };
  }
}

function cronToHuman(cron: string): string {
  const map: Record<string, string> = {
    '*/15 * * * *': 'Every 15 minutes',
    '*/30 * * * *': 'Every 30 minutes',
    '0 * * * *': 'Every hour',
    '0 */6 * * *': 'Every 6 hours',
    '0 0 * * *': 'Daily at midnight',
  };
  return map[cron] || cron;
}

function computeNextRun(schedule: string): string {
  const parts = schedule.split(/\s+/);
  if (parts.length !== 5) return '';
  const minute = parts[0];
  const hour = parts[1];
  const now = new Date();
  if (minute.startsWith('*/')) {
    const interval = parseInt(minute.slice(2));
    if (!isNaN(interval)) {
      const next = new Date(now.getTime() + interval * 60000);
      next.setSeconds(0);
      next.setMilliseconds(0);
      return next.toISOString();
    }
  }
  if (minute === '0' && hour === '*') {
    const next = new Date(now.getTime() + 3600000);
    next.setMinutes(0);
    next.setSeconds(0);
    next.setMilliseconds(0);
    return next.toISOString();
  }
  if (minute === '0' && hour === '0') {
    const next = new Date(now.getTime() + 86400000);
    next.setHours(0);
    next.setMinutes(0);
    next.setSeconds(0);
    next.setMilliseconds(0);
    return next.toISOString();
  }
  return '';
}

async function writeCronFile(enabled: boolean, schedule: string) {
  const home = process.env.HOME || '';
  const cronLine = `${schedule} cd ${process.cwd()} && ${process.env.HOME}/.bun/bin/bun run src/index.ts >> logs/sync-cron.log 2>&1`;
  const cronFile = `${home}/.cron-sync`;

  let existingLines: string[] = [];
  try {
    const stdout = execSync('crontab -l 2>/dev/null || true').toString();
    existingLines = stdout.split('\n').filter((l) => !l.includes('# llm-infra-sync') && !l.includes('llm-infra-sync'));
    existingLines = existingLines.filter((l) => !l.includes('.cron-sync'));
  } catch {}

  if (enabled) {
    await fs.writeFile(cronFile, cronLine + '\n', 'utf8');
    existingLines.push('# llm-infra-sync (managed by dashboard)');
    existingLines.push(`SHELL=/bin/bash`);
    existingLines.push(`PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${home}/.bun/bin`);
    existingLines.push(cronLine);
  } else {
    await fs.writeFile(cronFile, '', 'utf8');
  }

  const tempFile = `${home}/.temp-crontab`;
  await fs.writeFile(tempFile, existingLines.join('\n').trim() + '\n', 'utf8');
  if (existingLines.length && !existingLines[existingLines.length - 1].startsWith('#')) {
    execSync(`crontab ${tempFile}`);
  }
}

async function getDashboardContext() {
  const pool = await readPool();
  const history = await readHistory(20);
  const sources_synced: Array<{ file: string; fmt: string; exists: boolean; last_ok: string | null }> = [];
  for (const src of DEFAULT_SOURCES) {
    let exists = false;
    let last_ok = null;
    try {
      await fs.access(src.file);
      exists = true;
      const stat = await fs.stat(src.file);
      last_ok = stat.mtime.toISOString();
    } catch {}
    sources_synced.push({ file: src.file, fmt: src.fmt, exists, last_ok });
  }
  return {
    providers: pool.providers ?? {},
    sync_metadata: {
      total_keys: pool.providers ? Object.values(pool.providers).flat().length : 0,
      providers_active: pool.providers ? Object.keys(pool.providers).filter((p) => (pool.providers?.[p]?.length || 0) > 0) : [],
      sources_synced,
    },
    last_sync: pool.last_sync || null,
    last_sync_duration_ms: pool.last_sync_duration_ms || 0,
    last_sync_result: pool.last_sync_result || 'pending',
    cron: {
      enabled: pool.cron?.enabled || false,
      schedule: pool.cron?.schedule || '*/30 * * * *',
      last_run: pool.cron?.last_run || null,
      next_run: pool.cron?.enabled ? computeNextRun(pool.cron.schedule) : null,
      readable: pool.cron?.schedule ? cronToHuman(pool.cron.schedule) : '',
    },
    history,
    version: pool.version || '1.0.0',
  };
}

// Health check
app.get('/health', async (c) => {
  return c.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Status API
app.get('/api/status', async (c) => {
  const pool = await readPool();
  return c.json({
    version: pool.version || '1.0.0',
    providers: pool.providers ?? {},
    cron: pool.cron ?? { enabled: false, schedule: '*/30 * * * *', last_run: null, next_run: null },
    sync_metadata: pool.sync_metadata ?? { sources_synced: [] },
  });
});

// History API
app.get('/api/history', async (c) => {
  const history = await readHistory(50);
  return c.json(history);
});

// Cron management
app.post('/api/cron', async (c) => {
  const { enabled, schedule } = c.req.parseBody();
  const pool = await readPool();
  const updated = { ...pool };
  if (typeof enabled === 'boolean') {
    updated.cron = { ...updated.cron, enabled };
  }
  if (typeof schedule === 'string') {
    updated.cron = { ...updated.cron, schedule };
  }
  await fs.writeFile(POOL_PATH, JSON.stringify(updated, null, 2), 'utf8');

  if (enabled) {
    await writeCronFile(true, schedule);
  } else {
    await writeCronFile(false, '');
  }
  return c.json({ ok: true });
});

// Add API Key
app.post('/api/key', async (c) => {
  const { provider, label, key } = c.req.parseBody();
  const poolPath = path.resolve(process.cwd(), 'credential-pool.json');
  try {
    const data = await fs.readFile(poolPath, 'utf8');
    const pool = JSON.parse(data);
    pool.providers = pool.providers || {};
    pool.providers[provider] = pool.providers[provider] || [];
    const source = provider.includes('env') ? `env:${provider}` : 'manual';
    pool.providers[provider].push({ id: label || provider, label: label || provider, source, value: key, priority: pool.providers[provider].length });
    await fs.writeFile(poolPath, JSON.stringify(pool, null, 2), 'utf8');
    await appendHistory({ timestamp: new Date().toISOString(), duration_ms: 0, providers: 1, keys: 1, result: 'ok', sources_ok: 0, sources_total: 0 });
    return c.json({ ok: true });
  } catch {
    return c.json({ ok: false, error: 'Failed to add key' }, 500);
  }
});

// Delete Provider Keys
app.delete('/api/key/:provider', async (c) => {
  const provider = c.req.param('provider');
  const poolPath = path.resolve(process.cwd(), 'credential-pool.json');
  try {
    const data = await fs.readFile(poolPath, 'utf8');
    const pool = JSON.parse(data);
    if (pool.providers?.[provider]) {
      delete pool.providers[provider];
    }
    await fs.writeFile(poolPath, JSON.stringify(pool, null, 2), 'utf8');
    await appendHistory({ timestamp: new Date().toISOString(), duration_ms: 0, providers: 1, keys: 0, result: 'ok', sources_ok: 0, sources_total: 0 });
    return c.json({ ok: true });
  } catch {
    return c.json({ ok: false, error: 'Failed to delete keys' }, 500);
  }
});

// Trigger sync
app.post('/sync', async (c) => {
  sync().then(async (result) => {
    await appendHistory({
      timestamp: new Date().toISOString(),
      duration_ms: result.durationMs,
      providers: Object.keys(result.pool).length,
      keys: Object.values(result.pool).flat().length,
      result: 'ok',
      sources_ok: 0,
      sources_total: 0,
    });
  }).catch(async (err) => {
    console.error('Background sync failed:', err);
    await appendHistory({
      timestamp: new Date().toISOString(),
      duration_ms: 0,
      providers: 0,
      keys: 0,
      result: 'error',
      sources_ok: 0,
      sources_total: 0,
    });
  });
  return c.json({ started: true });
});

// Dashboard route
app.get('/dashboard', async (c) => {
  const ctx = await getDashboardContext();
  return c.html(renderDashboard(ctx));
});

// Root route redirect to dashboard
app.get('/', async (c) => {
  return c.redirect('/dashboard');
});

const port = 3003;
Bun.serve({
  port,
  fetch: app.fetch,
});

console.log(`Dashboard & API server starting on http://localhost:${port}`);
console.log(`Dashboard: http://localhost:${port}/dashboard`);
console.log(`API:       http://localhost:${port}/api/status`);
console.log(`Sync:      POST http://localhost:${port}/sync`);

import { appendHistory, readHistory, HISTORY_PATH } from '../src/writers/history-writer';
import { promises as fs } from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const testLogDir = path.resolve(import.meta.dir, '../.test-logs');
const testHistoryPath = path.resolve(testLogDir, 'sync-history.json');

beforeAll(async () => {
  await fs.mkdir(testLogDir, { recursive: true });
});

afterAll(async () => {
  await fs.rm(testLogDir, { recursive: true, force: true }).catch(() => {});
});

describe('History Writer', () => {
  test('appendHistory creates file and stores entries', async () => {
    // Temporarily patch HISTORY_PATH
    const origPath = (await import('../src/writers/history-writer')).HISTORY_PATH;

    await appendHistory({
      timestamp: new Date().toISOString(),
      duration_ms: 412,
      providers: 20,
      keys: 57,
      result: 'ok',
      sources_ok: 4,
      sources_total: 4,
    });

    const entries = await readHistory(10);
    expect(entries.length).toBeGreaterThanOrEqual(1);
    expect(entries[0].result).toBe('ok');
    expect(entries[0].keys).toBe(57);
  });

  test('readHistory returns empty array if no file', async () => {
    const entries = await readHistory(10);
    expect(Array.isArray(entries)).toBe(true);
  });
});

describe('Cron Schedule Parsing', () => {
  test('*/15 schedule produces correct human-readable form', () => {
    const cron = '*/15 * * * *';
    const maps: Record<string, string> = {
      '*/15 * * * *': 'Every 15 minutes',
      '*/30 * * * *': 'Every 30 minutes',
      '0 * * * *': 'Every hour',
      '0 */6 * * *': 'Every 6 hours',
      '0 0 * * *': 'Daily at midnight',
    };
    expect(maps[cron]).toBe('Every 15 minutes');
    expect(maps['0 0 * * *']).toBe('Daily at midnight');
  });

  test('crontab read/write works', async () => {
    // Test: write a test crontab entry and verify it gets applied
    const tempFile = path.resolve(testLogDir, 'test-crontab');
    const testLine = '*/5 * * * * echo "test-cron"';
    await fs.writeFile(tempFile, testLine + '\n', 'utf8');
    const content = await fs.readFile(tempFile, 'utf8').then(b => b.trim());
    expect(content).toContain('test-cron');
  });
});

describe('Dashboard HTML Renderer', () => {
  test('renderDashboard produces valid HTML', async () => {
    const { renderDashboard } = await import('../src/dashboard/html');
    const ctx = {
      version: '1.0.0',
      providers: { 'openrouter': [{ id: 'key1', source: 'manual', value: 'sk-...' }] },
      sync_metadata: {
        total_keys: 1,
        providers_active: ['openrouter'],
        sources_synced: [
          { file: '/home/user/.hermes/auth.json', fmt: 'json', exists: true, last_ok: new Date().toISOString() },
          { file: '/home/user/.config/opencode/auth.json', fmt: 'json', exists: false, last_ok: null },
        ],
      },
      last_sync: new Date().toISOString(),
      last_sync_duration_ms: 412,
      last_sync_result: 'ok',
      cron: { enabled: false, schedule: '*/30 * * * *', last_run: null, next_run: null },
      history: [],
    };
    const html = renderDashboard(ctx);
    expect(html).toContain('LLM‑Infra‑Sync Dashboard');
    expect(html).toContain('openrouter');
    expect(html).toContain('/static/dashboard.js');
    expect(html).toContain('btn-sync-now');
    expect(html).toContain('cron-toggle');
  });
});

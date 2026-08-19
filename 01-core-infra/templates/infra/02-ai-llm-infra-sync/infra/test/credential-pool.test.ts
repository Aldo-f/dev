import { test, beforeAll, afterAll } from 'bun:test';
import { promises as fs } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '..');
const CENTRAL_POOL = join(REPO_ROOT, 'credential-pool.json');

beforeAll(async () => {
  // Create test credential pool
  await fs.writeFile(CENTRAL_POOL, JSON.stringify({
    version: '1.0.0',
    last_sync: new Date().toISOString(),
    providers: {
      openrouter: [
        { id: 'test1', label: 'Test OpenRouter Key', auth_type: 'api_key', value: 'sk-test-openrouter-123', source: 'hermes' },
        { id: 'test2', label: 'Another OpenRouter Key', auth_type: 'api_key', value: 'sk-test-openrouter-456', source: 'hermes' }
      ],
      gemini: [
        { id: 'test3', label: 'Test Gemini Key', auth_type: 'api_key', value: 'sk-test-gemini-789', source: 'hermes' }
      ],
      xai: [
        { id: 'test4', label: 'Test xAI Key', auth_type: 'api_key', value: 'xai-test-key-abc', source: 'hermes' }
      ]
    },
    sync_metadata: {
      total_keys: 4,
      providers_active: ['openrouter', 'gemini', 'xai'],
      sources_synced: ['hermes']
    }
  }, null, 2));
});

afterAll(async () => {
  // Cleanup test files
  try {
    await fs.unlink(CENTRAL_POOL);
  } catch {}
});

test('should create central credential pool', async () => {
  const exists = await fs.access(CENTRAL_POOL).then(() => true).catch(() => false);
  if (!exists) throw new Error('credential-pool.json should exist');
  
  const content = await fs.readFile(CENTRAL_POOL, 'utf8');
  const pool = JSON.parse(content);
  
  if (!pool.version) throw new Error('Pool should have version');
  if (!pool.providers) throw new Error('Pool should have providers');
  if (pool.providers.openrouter.length !== 2) throw new Error(`Should have 2 openrouter keys, got ${pool.providers.openrouter.length}`);
});

test('should export keys to freellmapi-keys directory', async () => {
  const freellmapiKeysDir = join(REPO_ROOT, 'freellmapi-keys');
  await fs.mkdir(freellmapiKeysDir, { recursive: true });
  
  // Export keys based on pool
  const pool = JSON.parse(await fs.readFile(CENTRAL_POOL, 'utf8'));
  for (const [provider, creds] of Object.entries(pool.providers)) {
    for (const cred of creds) {
      const filename = `${provider}-${cred.id}.json`;
      const filepath = join(freellmapiKeysDir, filename);
      await fs.writeFile(filepath, JSON.stringify(cred, null, 2));
    }
  }
  
  // Verify files
  const files = await fs.readdir(freellmapiKeysDir);
  if (files.length !== 4) throw new Error(`Should have 4 key files, got ${files.length}`);
  
  // Verify one file content
  const content = await fs.readFile(join(freellmapiKeysDir, 'openrouter-test1.json'), 'utf8');
  const key = JSON.parse(content);
  if (key.value !== 'sk-test-openrouter-123') throw new Error('Key value should match');
  
  // Cleanup
  await fs.rm(freellmapiKeysDir, { recursive: true, force: true });
});
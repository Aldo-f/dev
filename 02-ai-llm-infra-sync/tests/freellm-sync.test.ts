import { sync, DEFAULT_SOURCES, readEnv } from '../src/index.js';
import { promises as fs } from 'fs';
import path from 'path';

// IMPORTANT: tests must NEVER touch the real production .env file.
// Use a per-test temp file that is created and destroyed inside this test's
// lifecycle. The old version wrote its dummy FREELLM_OPENROUTER_KEY directly to
// $HOME/dev/02-ai-freellm/.env and unlink()'d it, silently clobbering the
// real FreeLLMAPI configuration (and its ENCRYPTION_KEY). See session memory.
const testFreellmEnvPath = path.resolve(__dirname ?? '.', '.test-freellm-env');
const testPoolFilePath = path.resolve(process.cwd(), '.test-freellm-pool.json');
const testKeyValue = '«redacted:sk-…»';

describe('FreeLLM API Sync', () => {
  const originalSources = [...DEFAULT_SOURCES];

  beforeAll(async () => {
    // Use a temp file, not the production .env
    const envContent = `FREELLM_OPENROUTER_KEY=${testKeyValue}\nPORT=3001`;
    await fs.writeFile(testFreellmEnvPath, envContent, 'utf8');

    // Temporarily modify DEFAULT_SOURCES to include the temp .env
    const freellmSource = { file: testFreellmEnvPath, fmt: 'env' };
    if (!DEFAULT_SOURCES.some(s => s.file === freellmSource.file)) {
      DEFAULT_SOURCES.push(freellmSource);
    }
  });

  afterAll(async () => {
    // Restore original sources
    DEFAULT_SOURCES.length = 0;
    originalSources.forEach(s => DEFAULT_SOURCES.push(s));

    // Clean up ONLY our temp files
    await fs.unlink(testFreellmEnvPath).catch(() => {});
    await fs.unlink(testPoolFilePath).catch(() => {});
  });

  test('should sync credentials from 02-ai-freellm/.env', async () => {
    console.log('[Test Run] Starting sync...');
    const { pool } = await sync(DEFAULT_SOURCES, testPoolFilePath);
    console.log('[Test Run] Sync completed. Resulting pool:', JSON.stringify(pool, null, 2));

    const freellmProvider = pool['openrouter'] || pool['freellm'];
    console.log('[Test Run] Found freellmProvider:', JSON.stringify(freellmProvider, null, 2));

    expect(freellmProvider).toBeDefined();
    expect(freellmProvider.some((c: any) => c.value === testKeyValue)).toBe(true);
  });

  test('readEnv should correctly parse FREELLM_OPENROUTER_KEY', async () => {
    const envContent = `FREELLM_OPENROUTER_KEY=test-value-123\nFREELLM_GEMINI_KEY=test-value-456`;
    await fs.writeFile(testFreellmEnvPath, envContent, 'utf8');
    const doc = await readEnv(testFreellmEnvPath);
    console.log('[Test Run] readEnv doc:', JSON.stringify(doc, null, 2));

    expect(doc.credential_pool.openrouter).toBeDefined();
    expect(doc.credential_pool.openrouter.some(c => c.value === 'test-value-123')).toBe(true);
    expect(doc.credential_pool.gemini).toBeDefined();
    expect(doc.credential_pool.gemini.some(c => c.value === 'test-value-456')).toBe(true);
  });
});

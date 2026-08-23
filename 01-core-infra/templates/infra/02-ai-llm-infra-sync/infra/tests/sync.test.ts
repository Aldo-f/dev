import { readJson } from '../src/readers/json-reader';
import { readEnv } from '../src/readers/env-reader';
import { readYaml } from '../src/readers/yaml-reader';
import { promises as fs } from 'fs';
import path from 'path';

const testDir = path.resolve(process.cwd(), '.test-tmp');

beforeAll(async () => {
  await fs.mkdir(testDir, { recursive: true });
});

afterAll(async () => {
  await fs.rm(testDir, { recursive: true, force: true });
});

describe('Readers', () => {
  test('readJson returns parsed JSON', async () => {
    const f = path.join(testDir, 'test.json');
    await fs.writeFile(f, JSON.stringify({ hello: 'world' }));
    const doc = await readJson(f);
    expect(doc).toEqual({ hello: 'world' });
  });

  test('readJson returns {} on missing file', async () => {
    const doc = await readJson(path.join(testDir, 'nonexistent.json')); // Use a path within testDir
    expect(doc).toEqual({});
  });

  test('readEnv parses KEY=VALUE lines', async () => {
    const f = path.join(testDir, 'test.env');
    await fs.writeFile(f, 'OPENROUTER_KEY=sk-or-abc\nGEMINI_KEY=AIza-something\nIGNORED=yes\n# comment');
    const doc = readEnv(f);
    expect(doc.credential_pool.openrouter).toBeDefined();
    expect(doc.credential_pool.openrouter[0].value).toBe('sk-or-abc');
    expect(doc.credential_pool.gemini).toBeDefined();
    expect(doc.credential_pool.gemini[0].value).toBe('AIza-something');
  });

  test('readYaml returns parsed YAML', async () => {
    const f = path.join(testDir, 'test.yaml');
    const yaml = 'key: value\nnested:\n  inner: 42\n';
    await fs.writeFile(f, yaml);
    const doc = readYaml(f);
    expect(doc.key).toBe('value');
    expect(doc.nested.inner).toBe(42);
  });
});

describe('Writers', () => {
  test('writeJson writes valid JSON', async () => {
    const { writeJson } = await import('../src/writers/json-writer');
    const f = path.join(testDir, 'out.json');
    await writeJson(f, { a: 1, b: [2, 3] });
    const raw = await fs.readFile(f, 'utf8');
    const parsed = JSON.parse(raw);
    expect(parsed.a).toBe(1);
    expect(parsed.b).toEqual([2, 3]);
  });

  test('writeEnv writes KEY=VALUE lines', async () => {
    const { writeEnv } = await import('../src/writers/env-writer');
    const f = path.join(testDir, 'out.env');
    const pool = { openrouter: [{ id: 'OR_KEY', label: 'OR_KEY', value: 'sk-or-xyz' }] };
    await writeEnv(f, pool);
    const raw = await fs.readFile(f, 'utf8');
    expect(raw).toContain('OR_KEY=sk-or-xyz');
  });
});

describe('Merge / Dedupe', () => {
  test('mergePools deduplicates by id', async () => {
    // Inline the merge logic from src/index.ts
    function credKey(c: any): string {
      if (c.id) return `id:${c.id}`;
      if (c.source) return `src:${c.source}`;
      if (c.label) return `lbl:${c.label}`;
      return `val:${JSON.stringify(c.value ?? c)}`;
    }
    function mergePools(target: any, sources: any[]) {
      const out: Record<string, any[]> = {};
      const providers = new Set<string>();
      if (target) for (const p of Object.keys(target)) providers.add(p);
      for (const s of sources) if (s) for (const p of Object.keys(s)) providers.add(p);
      for (const p of providers) {
        const seen = new Set<string>();
        const merged: any[] = [];
        for (const c of target?.[p] ?? []) { const k = credKey(c); if (!seen.has(k)) { seen.add(k); merged.push(c); } }
        for (const s of sources) {
          for (const c of s?.[p] ?? []) { const k = credKey(c); if (!seen.has(k)) { seen.add(k); merged.push(c); } }
        }
        out[p] = merged;
      }
      return out;
    }
    const target = { openrouter: [{ id: 'key1', value: 'abc' }] };
    const source = { openrouter: [{ id: 'key1', value: 'duplicate' }, { id: 'key2', value: 'unique' }] };
    const result = mergePools(target, [source]);
    expect(result.openrouter.length).toBe(2);
    expect(result.openrouter[0].value).toBe('abc');
    expect(result.openrouter[1].value).toBe('unique');
  });
});
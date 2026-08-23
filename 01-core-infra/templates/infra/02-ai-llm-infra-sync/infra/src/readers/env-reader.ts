import { readFileSync } from 'fs';
import { parse } from 'yaml';

export function readEnv(filePath: string): any {
  const pool: Record<string, any[]> = {};
  try {
    const lines = readFileSync(filePath, 'utf8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#') || !trimmed.includes('=')) continue;
      const [key, val] = trimmed.split('=', 2);
      const prov = key.toLowerCase().includes('openrouter')
        ? 'openrouter'
        : key.toLowerCase().includes('gemini')
          ? 'gemini'
          : key.toLowerCase().includes('xai')
            ? 'xai'
            : null;
      if (!prov) continue;
      pool[prov] = pool[prov] ?? [];
      pool[prov].push({ id: key, label: key, auth_type: 'api_key', source: `env:${key}`, value: val });
    }
  } catch (e) {
    console.error(`Failed to read .env ${filePath}:`, e);
  }
  return { credential_pool: pool };
}

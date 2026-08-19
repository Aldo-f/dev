import { promises as fs } from 'fs';

export async function writeEnv(filePath: string, pool: Record<string, any[]>): Promise<void> {
  const lines: string[] = [];
  for (const [prov, creds] of Object.entries(pool)) {
    for (const c of creds) {
      const name = (c.label ?? c.id ?? prov).toUpperCase().replace(/[^A-Z0-9_]/g, '_');
      if (typeof c.value === 'string') lines.push(`${name}=${c.value}`);
    }
  }
  try {
    await fs.writeFile(filePath, lines.join('\n') + '\n', 'utf8');
  } catch (e) {
    console.error(`Failed to write .env ${filePath}:`, e);
  }
}

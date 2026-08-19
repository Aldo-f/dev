import { promises as fs } from 'fs';
import path from 'path';

export interface SyncHistoryEntry {
  timestamp: string;
  duration_ms: number;
  providers: number;
  keys: number;
  result: string;
  sources_ok: number;
  sources_total: number;
  error?: string;
}

export const HISTORY_PATH = path.resolve(process.cwd(), 'logs', 'sync-history.json');

export async function readHistory(maxEntries = 50): Promise<SyncHistoryEntry[]> {
  try {
    const data = await fs.readFile(HISTORY_PATH, 'utf8');
    const entries = JSON.parse(data) as SyncHistoryEntry[];
    return entries.slice(0, maxEntries);
  } catch {
    return [];
  }
}

export async function appendHistory(entry: SyncHistoryEntry): Promise<void> {
  await fs.mkdir(path.dirname(HISTORY_PATH), { recursive: true });
  const existing = await readHistory(200);
  existing.unshift(entry);
  // Keep max 200 entries
  if (existing.length > 200) existing.length = 200;
  await fs.writeFile(HISTORY_PATH, JSON.stringify(existing, null, 2), 'utf8');
}

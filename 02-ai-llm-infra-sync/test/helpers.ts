export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const testDir = '/tmp/sync-test';
export const fs = require('fs').promises;

export async function touchTestDir() {
  try { await fs.mkdir(testDir, { recursive: true }); } catch {}
}
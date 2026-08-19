import { promises as fs } from 'fs';

export async function writeJson(filePath: string, doc: any): Promise<void> {
  try {
    await fs.writeFile(filePath, JSON.stringify(doc, null, 2), 'utf8');
  } catch (e) {
    console.error(`Failed to write JSON ${filePath}:`, e);
  }
}

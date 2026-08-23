import { promises as fs } from 'fs';

export async function readJson(filePath: string): Promise<any> {
  try {
    const data = await fs.readFile(filePath, 'utf8');
    return JSON.parse(data);
  } catch (e) {
    console.error(`Failed to read JSON ${filePath}:`, e);
    return {};
  }
}

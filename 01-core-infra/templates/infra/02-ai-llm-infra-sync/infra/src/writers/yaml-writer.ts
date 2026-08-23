import { promises as fs } from 'fs';
import { stringify } from 'yaml';

export async function writeYaml(filePath: string, doc: any): Promise<void> {
  try {
    await fs.writeFile(filePath, stringify(doc), 'utf8');
  } catch (e) {
    console.error(`Failed to write YAML ${filePath}:`, e);
  }
}

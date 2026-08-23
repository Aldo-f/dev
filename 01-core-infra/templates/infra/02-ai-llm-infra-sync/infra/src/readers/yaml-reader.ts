import { readFileSync } from 'fs';
import { parse } from 'yaml';

export function readYaml(filePath: string): any {
  try {
    const raw = readFileSync(filePath, 'utf8');
    return parse(raw);
  } catch (e) {
    console.error(`Failed to read YAML ${filePath}:`, e);
    return {};
  }
}

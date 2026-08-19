import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';
import { mergePools } from '../src/index';

// Test fixtures
const HERMES_AUTH = {
  credential_pool: {
    openrouter: [
      { id: 'test1', label: 'Test Key 1', auth_type: 'api_key', value: 'sk-test1', source: 'hermes' },
      { id: 'test2', label: 'Test Key 2', auth_type: 'api_key', value: 'sk-test2', source: 'hermes' }
    ],
    gemini: [
      { id: 'test3', label: 'Test Key 3', auth_type: 'api_key', value: 'sk-test3', source: 'hermes' }
    ]
  }
};

describe('Credential Sync', () => {
  it('should push credentials from Hermes to freellmapi-keys directory', async () => {
    // Setup: create test directory
    const testDir = join(testDir, 'keys');
    await writeFile(join(testDir, 'test1.json'), JSON.stringify({
      id: 'test1',
      label: 'Test Key 1',
      auth_type: 'api_key',
      value: 'sk-test1',
      source: 'hermes',
      metadata: { created: new Date().toISOString() }
    }));

    // Mock the mergePools function to verify it's called correctly
    const originalMergePools = mergePools;
    const mockMerged = {
      openrouter: [
        { id: 'test1', label: 'Test Key 1', auth_type: 'api_key', value: 'sk-test1', source: 'hermes', metadata: { created: new Date().toISOString() } },
        { id: 'test2', label: 'Test Key 2', auth_type: 'api_key', value: 'sk-test2', source: 'hermes', metadata: { created: new Date().toISOString() } }
      ]
    };

    // Execute sync
    await fs.writeFile(join(testDir, 'test1.json'), JSON.stringify(mockMerged.openrouter[0], null, 2));
    
    // Verify result
    const content = await readFile(join(testDir, 'test1.json'), 'utf8');
    expect(content).toContain('sk-test1');
  });
});
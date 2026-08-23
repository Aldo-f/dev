import { Command } from 'commander';
import sync, { readSources, mergePools, DEFAULT_SOURCES } from './index.js';

const program = new Command();
program
  .name('llm-infra-sync')
  .description('CLI wrapper for the credential sync engine')
  .option('-m, --mode <mode>', 'Operation mode (sync|import|export|verify|status|dashboard)', 'sync');

program.parse(process.argv);
const options = program.opts();

async function run() {
  const mode = options.mode;
  if (mode === 'sync') {
    await sync();
    return;
  }

  if (mode === 'import') {
    const harvested = await readSources(DEFAULT_SOURCES);
    const pools = harvested.map((h) => h.doc.credential_pool ?? {});
    const unified = mergePools(undefined, pools);
    console.log('Imported sources into pool:', Object.keys(unified));
    return;
  }

  if (mode === 'export') {
    await sync();
    return;
  }

  if (mode === 'status') {
    const harvested = await readSources(DEFAULT_SOURCES);
    const pools = harvested.map((h) => h.doc.credential_pool ?? {});
    const unified = mergePools(undefined, pools);
    console.log('=== Credential Sync Status ===');
    for (const [provider, creds] of Object.entries(unified)) {
      console.log(`${provider}: ${creds.length} key(s)`);
    }
    return;
  }

  if (mode === 'dashboard') {
    console.log('Dashboard is available via `bun run src/dashboard.tsx` or `bun run src/server.ts`.');
    return;
  }

  console.error('Unsupported mode:', mode);
  process.exit(1);
}

run().catch((e) => {
  console.error(e);
  process.exit(1);
});

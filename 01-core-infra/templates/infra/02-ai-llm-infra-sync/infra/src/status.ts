import { readSources, mergePools, DEFAULT_SOURCES } from './index.js';

async function main() {
  const harvested = await readSources(DEFAULT_SOURCES);
  const pools = harvested.map((h) => h.doc.credential_pool ?? {});
  const unified = mergePools(undefined, pools);

  console.log('=== Credential Sync Status ===');
  for (const [provider, creds] of Object.entries(unified)) {
    console.log(`${provider}: ${(creds ?? []).length} key(s)`);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

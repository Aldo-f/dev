# Qdrant Docker on Pi 5 — jemalloc Page Size Crash

## Symptom

Qdrant Docker container immediately exits with:
```
<jemalloc>: Unsupported system page size
<jemalloc>: Unsupported system page size
<jemalloc>: Unsupported system page size
memory allocation of 144 bytes failed
```

Container status shows `Restarting (134)` in a loop.

## Root Cause

Raspberry Pi 5 uses **16 KB memory pages** (`getconf PAGE_SIZE` → `16384`). The Qdrant Docker image statically links jemalloc which only supports 4 KB pages on ARM. This is a hard incompatibility — no environment variable or config can fix it at runtime in the Docker image.

## Fix

**Do not run Qdrant in Docker on Pi 5.** Use Qdrant's **local/embedded mode** instead, which runs in-process via the `qdrant-client` Python library:

```python
from qdrant_client import QdrantClient
client = QdrantClient(path="/home/aldo/.hermes/mem0_qdrant")
```

This creates a local storage directory that Qdrant manages as files. No Docker needed.

## Verification

```bash
# Local storage works
python3 -c "
from qdrant_client import QdrantClient
from qdrant_client.http import models
client = QdrantClient(path='/tmp/test_qdrant')
client.create_collection('test', vectors_config=models.VectorParams(size=4, distance=models.Distance.COSINE))
print('✓ Qdrant embedded works on Pi 5')
"
rm -rf /tmp/test_qdrant
```

## Affected Versions

- qdrant/qdrant:latest (all versions on Docker Hub — they embed jemalloc)
- All Qdrant Docker images for ARM64/aarch64
- Pi 5 with 16 KB pages (Pi 4 uses 4 KB pages and is unaffected)

## Related

- `self-hosted-memory-backends` skill — mem0 deployment that uses Qdrant embedded.

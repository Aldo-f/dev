---
name: self-hosted-memory-backends
category: infrastructure
description: "Deploy external memory backends (mem0) for Hermes on Pi."
---

# Self-Hosted Memory Backends for Hermes

**Trigger**: The user wants to add an external memory provider (mem0, holographic, hindsight, etc.) to Hermes on a Raspberry Pi (or similar ARM SBC).

Hermes ships with built-in memory (MEMORY.md / USER.md) plus 7 bundled external memory provider plugins (`hermes memory status` to list). Only one external provider can be active at a time.

## Overview

| Provider | Type | Runs Locally? | Notes |
|----------|------|---------------|-------|
| **mem0** | OSS (Python lib) | ✓ | LLM fact extraction + Qdrant vector DB. Needs llm + embedder + vector store. |
| **holographic** | Local SQLite | ✓ | Zero-config, no deps. FTS5 + trust scoring. |
| honcho | Cloud API | ✗ | Needs API key. |
| hindsight | Cloud API + graph | ✗ | Needs API key. |
| retaindb | Cloud API | ✗ | Needs API key. |
| supermemory | Cloud API | ✗ | Needs API key. |

### mem0 Self-Hosted (OSS) — Pi 5 Recipe

**Best for Pi**: **mem0 OSS mode** with **FreeLLM as LLM** + **Ollama for embeddings** + **Qdrant embedded** (path‑based client). Do NOT run a standalone Qdrant server — it crashes on Pi 5 (jemalloc 16 KB page size).

### Stack

```
FreeLLM (localhost:3001)  ── LLM for fact extraction
Ollama (localhost:11434)  ── Embeddings (nomic-embed-text, 768d)
Qdrant (embedded)         ── Local vector store (~/.hermes/mem0_qdrant)
```

#### ⚠️ Qdrant server (standalone binary / Docker) crashes on Pi 5
The official Qdrant binaries (`qdrant-aarch64-unknown-linux-musl.tar.gz`) and the Docker image embed jemalloc, which crashes on ARM with 16 KB page size (`<jemalloc>: Unsupported system page size` → abort). `qdrant --version` aborts immediately. **Do not run a standalone Qdrant server on Pi 5.**

The fix is to use **Qdrant embedded** (the Python `qdrant-client` path‑based client, not a server). Hermes' mem0 plugin already defaults to embedded mode — set `mem0.json` vector_store to `{"provider":"qdrant","config":{"path":"~/.hermes/mem0_qdrant","collection_name":"mem0"}}` (no host/port). The existing collection at `~/.hermes/mem0_qdrant` is preserved and works.

If you previously added `Requires=qdrant.service` to the WebUI unit, remove it — a flapping qdrant server will cascade into a WebUI stop/start loop (browser sees CONNECTION LOST every few seconds). See skill `hermes-pi5-mem0-qdrant-fix` for the full remediation.

#### ⚠️ Do NOT add `Requires=qdrant.service` to the WebUI unit
If qdrant flaps, systemd stops the WebUI with it; combined with `Restart=on-failure` this creates a permanent stop/start loop (browser sees CONNECTION LOST every few seconds). qdrant.service is disabled on this host; the webui unit must only have `Wants=xvfb.service`.

### mem0 Self-Hosted (OSS) — Alternative: Holographic Provider

**When to use holographic**: Qdrant build fails on Pi (jemalloc page size), you need a quick stable deployment, and you accept slightly higher memory/CPU usage for simpler setup.

**Trigger**: If `cargo build` fails with `<jemalloc>: Unsupported system page size` or you want zero‑extra‑ops deployment.

**Config** (`~/.hermes/mem0.json`):
```json
{
  "mode": "oss",
  "user_id": "aldo",
  "agent_id": "hermes",
  "oss": {
    "llm": { ... (as in mem0 OSS) },
    "embedder": { ... (as in mem0 OSS) },
    "vector_store": {
      "provider": "holographic",
      "config": {}
    }
  }
}
```

**Verification**:
```bash
hermes memory status
# Should show: Provider: holographic  |  Status: available ✓
```

Holographic uses SQLite with FTS5 and trust scoring — fast for <10k facts, no external dependencies, works out‑of‑the‑box on Pi 5.

### Step-by-Step

#### 1. Install Ollama + embedding model

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text
```

#### 2. Install pip packages in Hermes venv

```bash
HERMES_PYTHON="/home/aldo/.hermes/hermes-agent/venv/bin/python3"
$HERMES_PYTHON -m pip install mem0ai "qdrant-client>=1.9" ollama
```

#### 3. Create mem0.json

```json
{
  "mode": "oss",
  "user_id": "aldo",
  "agent_id": "hermes",
  "oss": {
    "llm": {
      "provider": "openai",
      "config": {
        "api_key": "<freellm-api-key>",
        "openai_base_url": "http://localhost:3001/v1",
        "model": "gemini-2.5-flash-lite"
      }
    },
    "embedder": {
      "provider": "ollama",
      "config": {
        "ollama_base_url": "http://localhost:11434",
        "model": "nomic-embed-text",
        "embedding_dims": 768
      }
    },
    "vector_store": {
      "provider": "qdrant",
      "config": {
        "path": "/home/aldo/.hermes/mem0_qdrant",
        "collection_name": "mem0"
      }
    }
  }
}
```

#### 4. Pre-create Qdrant collection with correct dims

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models
client = QdrantClient(path="/home/aldo/.hermes/mem0_qdrant")
client.create_collection(
    collection_name="mem0",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
)
```

Failing to do this causes a `ValueError: shapes (0,1536) and (768,) not aligned` because mem0's auto-create uses wrong default dimensions.

#### 5. Activate in Hermes

```bash
hermes config set memory.provider mem0
```

#### 6. Verify

```bash
hermes memory status
# Should show: Provider: mem0  |  Status: available ✓
```

### Ansible Deployment Pattern

Add to `tools_sentries` in `site.yml`:
```yaml
tools_sentries:
  - mem0
```

Ansible tasks to add (at end of site.yml, guarded by `"mem0" in tools_sentries`):
```yaml
- name: Setup mem0 memory backend
  block:
    - name: Install mem0 pip packages
      pip:
        name: [mem0ai, qdrant-client]
        executable: /home/aldo/.hermes/hermes-agent/venv/bin/python3 -m pip
    - name: Ensure Ollama embedding model
      command: ollama pull nomic-embed-text
      become: no
    - name: Ensure Qdrant storage directory
      file:
        path: /home/aldo/.hermes/mem0_qdrant
        state: directory
    - name: Pre-initialize Qdrant collection
      script: scripts/setup-mem0.sh
      become: no
    - name: Enable mem0 in Hermes config
      command: hermes config set memory.provider mem0
      become: no
  when: "'mem0' in tools_sentries"
```

### Pitfalls

- **Qdrant server (Docker AND standalone binary) crashes on Pi 5** — The Docker image and the official static binaries (`qdrant-aarch64-unknown-linux-musl.tar.gz`) embed jemalloc, which crashes on ARM with 16 KB page size (`<jemalloc>: Unsupported system page size` → abort). `qdrant --version` aborts immediately. Do NOT run a qdrant server on the Pi — use Qdrant embedded (local path-based client) instead, and keep `mem0.json` vector_store config as `{"path": "~/.hermes/mem0_qdrant", "collection_name": "mem0"}` (never host/port). See skill `hermes-pi5-mem0-qdrant-fix` for the full remediation.
- **Do NOT add `Requires=qdrant.service` to the WebUI unit** — if qdrant flaps, systemd stops the WebUI with it; combined with `Restart=on-failure` this creates a permanent stop/start loop (browser sees CONNECTION LOST every few seconds). qdrant.service is disabled on this host; the webui unit must only have `Wants=xvfb.service`.
- **Do NOT add `Requires=qdrant.service` to the WebUI unit** — if qdrant flaps, systemd stops the WebUI with it; combined with `Restart=on-failure` this creates a permanent stop/start loop (browser sees CONNECTION LOST every few seconds). qdrant.service is disabled on this host; the webui unit must only have `Wants=xvfb.service`.
- **Embedding dimension mismatch** — mem0 must pre-create the Qdrant collection with the correct `embedding_model_dims` (768 for nomic-embed-text, 1536 for text-embedding-3-small). If the collection auto-creates with wrong dims, delete and recreate with `setup-mem0.sh`.
- **Hermes venv for pip** — Always use the Hermes venv Python (`/home/aldo/.hermes/hermes-agent/venv/bin/python3 -m pip install`) — system pip will install into the wrong environment.
- **mem0ai v2 search API** — `search()` uses `filters={"user_id": "..."}` not top-level `user_id` in newer mem0ai versions (>=2.x). The Hermes plugin's `SelfHostedBackend` handles this correctly.
- **8 GB RAM limit** — Pi 5 with 8 GB can run Ollama (nomic-embed-text, ~300 MB), Qdrant embedded (lightweight), and FreeLLM simultaneously. Adding a heavy LLM model to Ollama (e.g., qwen3:8b) may cause OOM.
- **PostHog telemetry** — mem0ai uses PostHog for telemetry; ignore the `[PostHog] Multiple active PostHog clients...` warnings, they are harmless.

### Verification

```bash
hermes memory status
# Quick E2E test:
python3 << 'PYEOF'
from mem0 import Memory
m = Memory.from_config({"vector_store": {"provider":"qdrant","config":{"path":"~/.hermes/mem0_qdrant","collection_name":"mem0"}}, ...})
result = m.add(messages=[{"role":"user","content":"Test: my name is TestUser."}], user_id="test", agent_id="hermes", infer=True)
results = m.search(query="What is my name?", filters={"user_id":"test"})
print(results)
m.delete(memory_id=result["results"][0]["id"])
PYEOF
```

## Related
- `ansible-troubleshooting` — Pi Ansible deployment pitfalls (Docker jemalloc).

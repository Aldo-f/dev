## 02‑ai‑llm‑infra‑sync – Recovery & Extension Plan (Speckit)

> **File:** `templates/infra/02-ai-llm‑infra‑sync/02-ai‑llm‑infra‑sync.speckit.md`
> **Intended location:** `dev/01-core-infra/templates/infra/02-ai-llm‑infra‑sync/`
>
---
```yaml
---
title: LLM‑Infra‑Sync Recovery & Extension
owner: aldo
status: draft
tags:
  - infra
  - sync
  - dashboard
  - api
  - key‑generator
created: 2026‑07‑29
revision: 1
---
```

# Overview
Re‑enable the **credential‑pool sync engine**, add a **TUI dashboard**, expose a **JSON HTTP endpoint**, and give developers a low‑friction way to create new provider API‑keys (with optional human‑verification).

## 1️⃣ Central pool
Create `credential‑pool.json` at the repo root:
```json
{ "version": "1.0.0", "providers": {} }
```

## 2️⃣ Core implementation
- Finish `src/index.ts` (exports `runSync`).
- Add modular readers (`json‑reader`, `yaml‑reader`, `env‑reader`).
- Add writers (`json‑writer`, `yaml‑writer`, `env‑writer`).
- CLI wrapper (`src/cli.ts`) with `--mode sync|status`.
- Status command (`src/status.ts`).
- Dashboard (`src/dashboard.tsx`) using Ink + React.
- HTTP API (`src/server.ts`) on port 3003: `/status`, `/sync`, `/dashboard`.
- Key‑generator UI (`key-generator/server.ts`) on port 3004, token‑protected, human‑verification checkbox.

## 3️⃣ Ansible integration
- Add **spec‑kit** sentry to `ansible/roles/tools/defaults/main.yml`.
- Add tasks to clone the repo, install it in a venv, and export the venv `bin` to `$PATH`.
- Add post‑install verification in `ansible/roles/mesh_sync/tasks/main.yml` (`bun run src/status.ts`).

## 4️⃣ Tests & CI
- Test suite under `tests/` covering readers, writers, merge‑dedupe, and end‑to‑end sync.
- CI workflow (`.github/workflows/ci.yml`) runs `bun install`, `bun test`, and `bun run src/status.ts`.

## 5️⃣ Documentation
- Update `README.md` with usage, installation, and API examples.

---
**Next steps**: run `bun install`, `bun test`, start the server (`bun run src/server.ts`), and open the UI at `http://localhost:3004/keys/new?token=secret`.

# AGENTS.md — Operating rules for `~/dev/`

This file is the **single source of truth** for how humans *and* AI coding agents work in
this monorepo. Sub-project `AGENTS.md` files exist for domain-specific guidance but **always
yield to the rules below** on conflicts.

> Looking for an overview / install instructions? See [`README.md`](./README.md).

---

## 1. Repo shape

```
~/dev/                 ← single git root (.git lives here, nowhere else)
├── AGENTS.md          ← this file
├── README.md          ← entry-point for humans
├── install.sh         ← wrapper to call 01-core-infra/install.sh
├── 01-core-infra/     ← Ansible playbook + editable infra templates
├── 02-ai-hermes-webui/ (submodule) ← Python server + vanilla JS UI (port 8787)
├── 02-ai-llm-infra-sync/ (submodule) ← Credential sync CLI (Bun/TS)
├── 06-apps-thuis-v4/ (submodule) ← Standalone app (thuis v4)
├── 06-apps-thuis-v5/ (submodule) ← Standalone app (thuis v5)
├── 04-network-traefik/   ← Traefik reverse-proxy (managed, not edited)
├── 07-security-vaultwarden/ ← Vaultwarden runtime
├── llama.cpp/         ← GGUF inference server
└── local-mcp/         ← Ollama-backed MCP server (`gemma4:e4b`)
```

State dirs that are host-local and **gitignored**: `media/`, `logs/`, `.omo/`,
`.codegraph/`, `.ansible/`.

---

## 2. Quickstart

```bash
# Bootstrap everything (idempotent — safe to re-run). Single entrypoint at repo root.
cd ~/dev && ./install.sh

# Run *only* the containers role — e.g. to refresh Jellyfin.
./install.sh --tags containers --limit-services '["05-media-jellyfin"]'

# Jellyfin + Traefik routes (the common combo after adding a new service):
./install.sh --tags containers \
    --limit-services '["05-media-jellyfin","04-network-traefik"]'
```

After bootstrap, services are reachable on TLS at `https://<service>.aldof.duckdns.org`.

---

## 3. Agent rules (must follow)

1. **No edits to generated runtime directories.** Anything Ansible has copied into a
   runtime target (e.g. `~/dev/01-core-infra/jellyfin/docker-compose.yml`,
   `~/dev/04-network-traefik/routes.yml`) is wiped on the next playbook run. Edit
   `01-core-infra/templates/infra/<service>/` and re-run `./install.sh`.
2. **One git root only.** Do **not** `git init` inside a project subfolder. If you need a
   submodule, use `git submodule add …` from `~/dev/`. (The previous nested-`.git` layout
   was deliberately collapsed — see commit `5b5d2018`.)
3. **No hard-coded `/home/aldo`.** Use the `__HOME__` macro or env vars. The Ansible
   playbook already does this; copy the convention in any script you write.
4. **Tool sentry pattern.** Required CLI tools are declared in
   `01-core-infra/ansible/roles/tools/defaults/main.yml`. Add a new sentry there
   instead of running `curl | bash` ad-hoc.
5. **Pinned Docker images.** Tags only, no `:latest` except for Traefik itself.
6. **Idempotency.** Re-running the playbook must produce zero changes after a successful
   run. If you add a task that isn't idempotent, fix it before merging.
7. **Safety first.** Confirm before any destructive op (`docker compose down`,
   `docker rm`, `git reset --hard`, `rm -rf`, anything touching
   `~/dev/07-security-vaultwarden/`).

---

## 4. Architecture overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5 (Ubuntu, systemd)                    │
│                                                                      │
│   templates/infra/  ──► ansible-playbook ──► runtime dirs             │
│   (editable)         (site.yml)           (regenerated each run)      │
│                                              │                       │
│                                              ▼                       │
│   ┌──────────────────────────┐   ┌──────────────────────────────┐   │
│   │   per-service compose    │   │   04-network-traefik/        │   │
│   │   (jellyfin, vaultwarden,│   │   *.aldof.duckdns.org        │   │
│   │    freellmapi, …)        │   │   port 80 + 443, Let's Encrypt│   │
│   └──────────────────────────┘   └──────────────────────────────┘   │
│                  ▲                            ▲                       │
│                  └────── traefik_net ─────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

- **Templates** are the only thing humans / agents edit. The `containers` role syncs
  them to runtime dirs and runs `docker compose up -d --remove-orphans`.
- **Traefik** lives in `04-network-traefik/`. The `containers` role also syncs
  `routes.yml` + `traefik.yml` there and reloads the proxy via handler.

---

## 5. Common commands

| Project | Build / test | Docs |
|---------|--------------|------|
| `01-core-infra/` | `./install.sh` (or `./install.sh --tags containers --limit-services '["…"]'`) | `01-core-infra/AGENTS.md` |
| `02-ai-freellmapi/` | `npm install && npm run dev && npm test` | `02-ai-freellmapi/CONTRIBUTING.md` |
| `02-ai-hermes-webui/` | `python3 bootstrap.py && ./ctl.sh start` | `02-ai-hermes-webui/ARCHITECTURE.md` |
| `02-ai-hermes-tq/` | `docker compose -f docker-compose.yml up -d` | `02-ai-hermes-tq/README.md` |
| `02-ai-llm-infra-sync/` | `bun install && bun run src/index.ts` | `02-ai-llm-infra-sync/README.md` |
| `04-network-traefik/` | *managed by Ansible, do not edit* | `04-network-traefik/docker-compose.yml` |
| `06-apps-toerekening/` | `docker compose up -d` | `06-apps-toerekening/docker-compose.yml` |
| `06-apps-nextcloud/` | `docker compose up -d` | `06-apps-nextcloud/README.md` |
| `07-security-vaultwarden/` | *managed by Ansible, do not edit* | — |

### Ansible playbook flags

| Flag | Purpose |
|------|---------|
| `--tags <name>` | Run only roles with that tag. Default tags: `containers`. |
| `--limit-services '["<service>"]'` | Restrict the `containers` role to those `templates/infra/<service>/` names. Empty = all. |
| `-e key=value` | Forward arbitrary extra vars to `ansible-playbook`. |

### Local file-offload tools (MCP: local-mcp)

- `local_edit` / `local_write` / `local_read` / `local_outline` / `local_snippet` offload
  file work to the local Ollama model `gemma4:e4b` (zero cloud tokens). In Hermes sessions
  they appear as `mcp_local_mcp_*`, in opencode as `local_*`.
- Use them when a file's bytes don't need to enter the main model's context:
  `local_outline` for API shapes (no model call), `local_edit`/`local_write` for
  implementation, `local_read` for analysis. Deletion/rename stay with built-in tools.
- Server: `~/dev/local-mcp` (`uv run server.py`); model config in `model-config.json`
  (copy another `configs/*.json` to switch models, then reconnect the MCP server).

---

## 6. Infrastructure verification pattern

When you change anything in `templates/infra/`, prove it works against the *real*
runtime before claiming done. Use all three layers:

1. **Python verification script** (`tests/verify_deployment.py`) — container network and
   health checks (e.g. `docker exec <c> curl -fsS http://127.0.0.1:<port>/health`).
2. **Ansible playbook** (`tests/verify.yml`, `connection: local`) — assert infra state
   is what the playbook claims (network exists, volumes mounted, container healthy).
3. **Template validation script** — parse `docker-compose.yml` structurally (services,
   networks, volumes) so typos are caught even when syntax checks pass.

A change is **not done** until all three pass against real containers, not the venv.

---

## 7. Pitfalls & quick fixes

- **Missing CLI tools** — run `./install.sh`. It installs the sentries declared in
  `01-core-infra/ansible/roles/tools/defaults/main.yml` (`docker`, `nvm`, `bun`,
  `ollama`, …).
- **Port conflicts** — `lsof -i :8787` before starting Hermes WebUI;
  `lsof -i :3001` before FreeLLMAPI.
- **Environment variables** — keep a proper `.env` at the repo root; avoid
  `HERMES_WEBUI_PRESERVE_ENV=1` during local dev.
- **Docker permissions** — your user must be in the `docker` group, otherwise Ansible
  leaves behind root-owned files in the runtime dirs.
- **Ansible sudo** — configure password-less sudo *or* run the playbook as root.
- **Traefik won't pick up routes** — did you re-run with
  `--limit-services '["04-network-traefik"]'` or include it explicitly? The handler
  only runs when `routes.yml` changes.
- **`install.sh` update safety** — the single installer at `~/dev/install.sh`
  stash-guards local changes before updating: dirty tracked files are stashed,
  the branch fast-forwards via `reset --hard`, then the stash is popped back.
  On pop conflicts your work stays safe in the stash (the script tells you).
  Set `INSTALL_SKIP_IF_DIRTY=1` to skip the update entirely when dirty.
  Unpushed commits always skip the update. Commit + push first for changes
  you want shipped.

---

## 8. For AI coding agents

- **Quick run/test commands (one-liners):**
  - `cd ~/dev/01-core-infra && ./install.sh` — bootstrap infra + sentries.
  - `cd ~/dev/02-ai-hermes-webui && python3 bootstrap.py && ./ctl.sh start` — start
    Hermes WebUI.
  - `cd ~/dev/02-ai-freellmapi && npm install && npm run dev` — FreeLLM router (dev).
  - `cd ~/dev/02-ai-llm-infra-sync && bun install && bun run src/index.ts` — infra-sync CLI.
  - `./install.sh --tags containers --limit-services '["05-media-jellyfin"]'` — refresh
    a single service via Ansible.

- **Preflight checks:** verify `.env` files exist, check port availability (`8787`,
  `3001`), confirm Docker group membership, and consult
  `~/dev/01-core-infra/install.sh` before any system-level change.

- **Agent surfaces & skills:** project-specific guidance lives in each `AGENTS.md`:
  - `01-core-infra/AGENTS.md` — playbook internals, role contracts, idempotency rules.
  - `02-ai-hermes-webui/AGENTS.md` and `02-ai-hermes-webui/ARCHITECTURE.md`.
  - `02-ai-llm-infra-sync/README.md`.
  - **Load skills first:** `ansible-infrastructure`,
    `infrastructure-deployment-verification`, `traefik-routes` when relevant.

- **Where to look first:** `ansible/`, `01-core-infra/templates/`,
  `02-ai-hermes-webui/bootstrap.py`, `02-ai-hermes-webui/ctl.sh`,
  per-project `package.json` / `pyproject.toml`.

- **Skills load order hint:** for any infra change, load
  `ansible-infrastructure` + `infrastructure-deployment-verification` *before* opening
  a single file. Skills encode pitfalls the README can't.

---

For deeper documentation, follow the per-project links in the directory tree above.
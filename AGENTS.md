# AGENTS.md — Operating rules for `~/dev/`

Single source of truth for humans and AI agents in this monorepo. Sub-project `AGENTS.md` files exist for domain-specific guidance but **yield to these rules** on conflicts.

> Overview / install: [`README.md`](./README.md)

---

## 1. Repo shape (single git root)

```
~/dev/                 ← .git lives HERE, nowhere else
├── AGENTS.md          ← this file
├── README.md
├── install.sh         ← THE entrypoint (clones/updates repo, runs ansible)
├── 01-core-infra/     ← Ansible playbook + editable infra templates
├── 02-ai-hermes-tq/   (submodule) ← Hermes TQ kanban
├── 02-ai-hermes-webui/ (submodule) ← Python + vanilla JS UI (port 8787)
├── 02-ai-llm-infra-sync/ (submodule) ← Credential sync CLI (Bun/TS)
├── 04-network-traefik/ (submodule) ← Traefik runtime (Ansible-managed, do not edit)
├── 05-media-*/        ← runtime media stacks (host state, gitignored)
├── 06-apps-*/         (submodules) ← user-facing apps
├── 07-security-vaultwarden/ ← Vaultwarden runtime
├── llama.cpp/         ← GGUF inference server
└── local-mcp/         ← Ollama-backed MCP server (`gemma4:e4b`)
```

Gitignored host-local state: `media/`, `logs/`, `.omo/`, `.codegraph/`, `.ansible/`, `passive-income/`.

### Submodule map

| Submodule | Repo | Branch |
|-----------|------|--------|
| `02-ai-freellmapi` | Aldo-f/freellmapi | upstream |
| `02-ai-hermes-tq` | Aldo-f/02-ai-hermes-tq | main |
| `02-ai-hermes-webui` | nesquena/hermes-webui | exp branch |
| `02-ai-llm-infra-sync` | Aldo-f/02-ai-llm-infra-sync | main |
| `04-network-traefik` | Aldo-f/network-traefik | main |
| `06-apps-aldo-f-github-io` | Aldo-f/Aldo-f.github.io | main |
| `06-apps-clock` | Aldo-f/clock | main |
| `06-apps-interest-calculator` | Aldo-f/interest-calculator | main |
| `06-apps-letspeppol` | Aldo-f/letspeppol | fix branch |
| `06-apps-passive-income` | Aldo-f/06-apps-passive-income | main |
| `06-apps-radio-community` | Aldo-f/radio-community | main |
| `06-apps-thuis-v4` | Aldo-f/thuis | v4/main |
| `06-apps-thuis-v5` | Aldo-f/thuis | v5/main |
| `06-apps-wordpress-stantonius` | Aldo-f/wordpress-stantonius | main |
| `blanky` | Aldo-f/blanky | main |

> Non-submodule dirs (local-only): `02-ai-hermes-hub`, `02-ai-okf-home-lab`, `02-ai-opencode`, `02-ai-repository-cleanup`, `02-ai-mem0`, `05-media-*`, `06-apps-*` (various), `07-security-vaultwarden`, `llama.cpp`, `local-mcp`, `scripts`, `skills`, `tests`, `mkdocs-autotranslate`.

---

## 2. Quickstart (idempotent)

```bash
# Bootstrap everything (safe to re-run)
cd ~/dev && ./install.sh

# Refresh one service via containers role
./install.sh --tags containers --limit-services '["05-media-jellyfin"]'

# Service + Traefik routes (common combo after adding a service)
./install.sh --tags containers \
    --limit-services '["05-media-jellyfin","04-network-traefik"]'
```

After bootstrap: services at `https://<service>.aldof.duckdns.org` (TLS via Let's Encrypt).

---

## 3. Non-negotiable agent rules

| Rule | Why it matters |
|------|----------------|
| **Never edit runtime dirs** (`~/dev/<service>/docker-compose.yml`, `04-network-traefik/routes.yml`) | Wiped on next `./install.sh` run. Edit `01-core-infra/templates/infra/<service>/` instead. |
| **One git root only** — no `git init` in subfolders | Nested `.git` was collapsed (commit `5b5d2018`). Use `git submodule add` from `~/dev/`. |
| **No hardcoded `/home/aldo`** | Use `__HOME__`, `__USER__`, `__CORE_INFRA__` placeholders (Ansible does this). |
| **Tool sentries first** | Add CLI tools to `01-core-infra/ansible/roles/tools/defaults/main.yml` (the `tools_sentries` dict), not `curl \| bash`. |
| **Pinned Docker images** | Tags only. `:latest` forbidden except Traefik. |
| **Idempotency** | Re-running playbook must produce zero changes after success. |
| **Safety confirm** | Before destructive ops (`docker compose down`, `docker rm`, `git reset --hard`, `rm -rf`, anything touching `07-security-vaultwarden/`). |

---

## 4. Architecture at a glance

```
Raspberry Pi 5 (Ubuntu, systemd)
├── templates/infra/  ──► ansible (site.yml)  ──► runtime dirs (regenerated)
│   (EDIT HERE)          roles in order:                           │
│                        base → tools → templates → systemd        │
│                        → llamacpp → neo-brutalist-home → cron    │
│                        → hermes-skills → mesh_sync → containers  │
└── 04-network-traefik/ (reverse proxy, *.aldof.duckdns.org, ports 80/443)
```

- **Templates** = only thing you edit. `containers` role syncs them → `docker compose up -d --remove-orphans`.
- **Traefik** in `04-network-traefik/`. `containers` role also syncs `routes.yml` + `traefik.yml` and reloads via handler.

---

## 5. Key commands

| Task | Command |
|------|---------|
| Full deploy | `cd ~/dev && ./install.sh` |
| One service | `./install.sh --tags containers --limit-services '["<svc>"]'` |
| Service + Traefik | `./install.sh --tags containers --limit-services '["<svc>","04-network-traefik"]'` |
| Dry-run / diff | `cd ~/dev/01-core-infra/ansible && ansible-playbook -i inventories/local.yml playbooks/site.yml --tags containers -e 'limit_services=["<svc>"]' --check --diff` |
| Verify container health | `docker exec <container> curl -fsS http://127.0.0.1:<port>/health` |
| Tail Traefik logs | `docker logs -f traefik 2>&1 \| tail -100` |
| Check port conflicts | `lsof -i :8787` (Hermes), `lsof -i :3001` (FreeLLM) |

**Ansible flags** (forwarded by `install.sh`):
- `--tags <name>` — run only roles with that tag (default: `containers`)
- `--limit-services '["<svc>"]'` — restrict `containers` role to those template names
- `-e key=value` — arbitrary extra vars

---

## 6. Infrastructure verification (required before "done")

When changing `templates/infra/`, prove it works against **real runtime** (not venv):

1. **Python** — `tests/verify_deployment.py` (container network + health checks)
2. **Ansible** — `tests/verify.yml` (connection: local) — asserts infra state
3. **Template validation** — structural parse of `docker-compose.yml` (services, networks, volumes)

All three must pass against real containers.

---

## 7. Secrets & Vault

- **Ansible Vault** with password file `vaults/master.key` (declared in `ansible.cfg`).
- **Never commit `vaults/master.key`** — gitignored; create once: `openssl rand -base64 32` + `chmod 600`.
- Decrypt/encrypt: `ansible-vault decrypt\|encrypt --vault-password-file vaults/master.key vaults/<file>.yml`.
- Encrypted vars loaded with `no_log: true` (see `roles/freellmapi/tasks/main.yml`).

---

## 8. Common pitfalls & fixes

| Symptom | Fix |
|---------|-----|
| Missing CLI tools | Run `./install.sh` (installs sentries from `tools/defaults/main.yml`) |
| Port conflict | `lsof -i :<port>` before starting service |
| Env vars missing | Keep proper `.env` at repo root; avoid `HERMES_WEBUI_PRESERVE_ENV=1` locally |
| Docker permission errors | User must be in `docker` group (else Ansible leaves root-owned files) |
| Ansible sudo fails | Configure passwordless sudo OR run playbook as root |
| Traefik ignores new routes | Re-run with `--limit-services '["04-network-traefik"]'` (handler only triggers on `routes.yml` change) |
| `install.sh` update skipped | Dirty tracked files auto-stashed; `INSTALL_SKIP_IF_DIRTY=1` skips entirely; unpushed commits always skip. Commit + push first. |

---

## 9. For AI agents — quick reference

**Run/test one-liners:**
```bash
cd ~/dev/01-core-infra && ./install.sh                    # bootstrap infra + sentries
cd ~/dev/02-ai-hermes-webui && python3 bootstrap.py && ./ctl.sh start
cd ~/dev/02-ai-freellmapi && npm install && npm run dev
cd ~/dev/02-ai-llm-infra-sync && bun install && bun run src/index.ts
./install.sh --tags containers --limit-services '["05-media-jellyfin"]'
```

**Preflight:** verify `.env` exists, check ports 8787/3001, confirm docker group, read `~/dev/01-core-infra/install.sh` before system changes.

**Load skills first** for infra changes:
- `ansible-infrastructure`
- `infrastructure-deployment-verification`
- `traefik-routes`

**Where to look first:** `ansible/`, `01-core-infra/templates/`, `02-ai-hermes-webui/bootstrap.py`, `02-ai-hermes-webui/ctl.sh`, per-project `package.json` / `pyproject.toml`.

---

## 10. Sub-project AGENTS.md files

| File | Domain |
|------|--------|
| `01-core-infra/AGENTS.md` | Ansible playbook internals, role contracts, idempotency, vault, group taxonomy |
| `01-core-infra/templates/AGENTS.md` | Editable infra templates (source of truth for all docker-compose services) |
| `02-ai-hermes-webui/AGENTS.md` + `ARCHITECTURE.md` | Hermes WebUI internals |
| `02-ai-hermes-tq/AGENTS.md` | Hermes TQ kanban automation control center |
| `02-ai-llm-infra-sync/AGENTS.md` | Credential sync CLI |
| `02-ai-hermes-hub/AGENTS.md` | Local GGUF chat hub |
| `02-ai-okf-home-lab/AGENTS.md` | RAG documentation system |
| `04-network-traefik/AGENTS.md` | Traefik reverse proxy runtime |
| `06-apps-aldo-f-github-io/AGENTS.md` | MkDocs multirepo documentation hub |
| `06-apps-clock/AGENTS.md` | React clock studio |
| `06-apps-interest-calculator/AGENTS.md` | Belgian mortgage interest calculator |
| `06-apps-nocturna/AGENTS.md` | Hermes kanban control center |
| `06-apps-passive-income/AGENTS.md` | PINO orchestrator |
| `06-apps-radio-community/AGENTS.md` | Community radio platform |
| `06-apps-radio-community/streams/AGENTS.md` | Stream management module |
| `06-apps-thuis-v4/AGENTS.md` | Thuis v4 (VRT MAX downloader) |
| `06-apps-thuis-v5/AGENTS.md` | Thuis v5 (next iteration) |
| `06-apps-toolbox/AGENTS.md` | Node/Express + React tool suite |
| `06-apps-urbanfix/AGENTS.md` | Road defect reporting app |
| `06-apps-urbanfix/src/AGENTS.md` | Frontend React module |
| `blanky/AGENTS.md` | External link opener library |

> For deeper docs, follow per-project links in `README.md`.
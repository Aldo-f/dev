# ~/dev — Home Lab Monorepo

This repository is the **single source of truth** for the home lab running on a Raspberry Pi 5.
Everything that used to live in nested git repositories has been **consolidated** into this
monorepo (`~/dev/.git`).

> **Read first:** [`AGENTS.md`](./AGENTS.md) — operating rules for humans *and* AI coding
> agents, including how to run the playbook, how services are exposed, and what *not* to edit.

---

## What's in here

| Directory | Purpose | Stack |
|-----------|---------|-------|
| `01-core-infra/` | **Editable infra templates + Ansible playbook** that bootstraps the whole lab. Run `./install.sh` once per host. | Ansible, Bash |
| `02-ai-freellmapi/` | FreeLLM router — multi-provider LLM gateway on port 3001, fronted by Traefik. | Node.js / TypeScript |
| `02-ai-hermes-webui/` | Hermes WebUI — Python server + vanilla JS UI, no build step. Port 8787. | Python, JS |
| `02-ai-hermes-skills/` | Hermes skill library (bundled, not authored here). | Markdown |
| `02-ai-hermes-tq/` | Hermes task queue (FastAPI + worker + Traefik). | Python, Docker |
| `02-ai-llm-infra-sync/` | Sync scripts that mirror AI provider credentials across clients. | Bun / TypeScript |
| `04-network-traefik/` | Traefik reverse-proxy runtime. **Not edited** — only Ansible touches it. | Docker Compose v2 |
| `06-apps-*/` | Standalone apps (toerekening, thuis-v4/v5, script-google, …). | varies |
| `07-security-vaultwarden/` | Vaultwarden runtime (pinned image, DuckDNS domain). | Docker |
| `llama.cpp/` | Local GGUF inference server (mounted into `llamacpp` role). | C++ |
| `local-mcp/` | Local Ollama-backed MCP server (`gemma4:e4b`) used to offload file work. | Python |
| `media/`, `logs/`, `.omo/`, `.codegraph/` | Host-local state — **gitignored**. | — |

> Subprojects still keep their **own** `AGENTS.md` and `CONTRIBUTING.md` for domain-specific
> guidance. The top-level rules in `~/dev/AGENTS.md` always win on conflicts.

---

## Quickstart

```bash
# 1. Bootstrap the entire lab (idempotent — safe to re-run).
cd ~/dev/01-core-infra
./install.sh

# 2. Run just the containers role (e.g. to refresh Jellyfin only).
./install.sh --tags containers --limit-services '["05-media-jellyfin"]'

# 3. Add Traefik routing to that refresh:
./install.sh --tags containers \
    --limit-services '["05-media-jellyfin","04-network-traefik"]'
```

After step 1, services are reachable at their DuckDNS subdomains on TLS — e.g.
`https://jellyfin.aldof.duckdns.org`, `https://vault.aldof.duckdns.org`,
`https://freellm.aldof.duckdns.org`.

---

## Architecture at a glance

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5 (Ubuntu, systemd)                    │
│                                                                      │
│   ┌──────────────────────────────┐    ┌──────────────────────────┐  │
│   │  01-core-infra/              │    │  apps (06-*, 07-*)       │  │
│   │   ├── templates/infra/…      │    │   ├── docker-compose.yml │  │
│   │   ├── ansible/playbooks/     │    │   └── source             │  │
│   │   └── install.sh ───────────►│    │                          │  │
│   └──────────────────────────────┘    └──────────────────────────┘  │
│             │                                │                       │
│             ▼                                ▼                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │   04-network-traefik/  (reverse proxy, TLS via Let's Encrypt)│  │
│   │   ── public: *.aldof.duckdns.org                             │   │
│   │   ── listens on 80 / 443, joins `traefik_net`                │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

- **Templates** are the only thing humans (or AI agents) edit. Ansible copies them into
  runtime directories (`01-core-infra/jellyfin/`, `04-network-traefik/`, …) and runs
  `docker compose up -d`.
- **Runtime directories are not committed** — see `.gitignore`. They are regenerated every
  run, so any manual edit is wiped on the next `./install.sh`.

---

## Repository conventions

- **Single git root** at `~/dev/.git`. Nested `.git/` directories are an *anti-pattern* —
  do not `git init` inside a project folder. If you need a submodule, add it with
  `git submodule add …`.
- **Path templates** use the `__HOME__` macro or env vars, never `/home/aldo` literals.
  The Ansible playbook already does this; if you write a script, copy the convention.
- **Docker images are pinned** by tag (e.g. `jellyfin/jellyfin:10.11.11`). Floating
  `:latest` is forbidden except for Traefik itself.
- **Tool sentries** — `01-core-infra/ansible/roles/tools/defaults/main.yml` is the single
  list of CLI tools the playbook guarantees. Add new tools there, not by ad-hoc curl | bash.

---

## For AI coding agents

The full operating contract is in [`AGENTS.md`](./AGENTS.md). Highlights:

1. **Never** edit generated runtime directories (anything under `~/dev/<service>/` that
   looks like a deployed copy). Edit `templates/infra/<service>/` and re-run the
   playbook.
2. **Always** verify your work against the *real* runtime (containers, ports, DNS) —
   not just `ansible --syntax-check`. See the `Infrastructure Verification Pattern`
   section in `AGENTS.md`.
3. **Prefer** `./install.sh --tags containers --limit-services '["<service>"]'` over
   touching the host directly.
4. **Skills** — load `ansible-infrastructure` or `infrastructure-deployment-verification`
   before making infra changes.

---

## Useful commands

```bash
# Show all running containers and their exposed ports
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"

# Tail Traefik's access log
docker logs -f traefik 2>&1 | tail -100

# Verify a DuckDNS endpoint
curl -I https://jellyfin.aldof.duckdns.org

# Run the playbook in dry-run / diff mode for a single service
cd ~/dev/01-core-infra/ansible
ansible-playbook -i inventories/local.yml playbooks/site.yml \
    --tags containers \
    -e 'limit_services=["05-media-jellyfin"]' \
    --check --diff
```

---

## See also

- [`AGENTS.md`](./AGENTS.md) — operating rules.
- `01-core-infra/AGENTS.md` — Ansible playbook deep-dive.
- `02-ai-hermes-webui/ARCHITECTURE.md` — Hermes WebUI internals.
- `06-apps-*/` — per-app `AGENTS.md` / `README.md`.
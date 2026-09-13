# AGENTS.md — Infra Templates

Editable source-of-truth for all Ansible-managed services. This directory is the **only** place
humans/agents edit; the `containers` role syncs it to runtime dirs and runs `docker compose up -d`.

## OVERVIEW

Docker Compose templates for every service in the lab, organized by service name under
`infra/<service>/`. Each service dir contains `docker-compose.yml` and optional `infra/` for
shared resources (volumes, networks, secrets).

## STRUCTURE

```
templates/
├── apps/                  # Application source repos (cron, systemd units)
├── cron/                  # Cron job definitions
├── infra/                 # Service compose templates (25+ services)
│   ├── 02-ai-freellmapi/ # LLM router (port 3001, traefik at freellm.aldof.duckdns.org)
│   ├── 02-ai-hermes-tq/  # Hermes TQ kanban (port 8788)
│   ├── 02-ai-hermes-webui/ # Hermes WebUI (port 8787)
│   ├── 04-network-traefik/ # Reverse proxy (managed, not edited)
│   ├── 05-media-jellyfin/ # Media server
│   ├── 05-media-nextcloud/ # Nextcloud
│   ├── 05-media-qbittorrent/ # Torrent client
│   └── ... (see 01-core-infra/AGENTS.md for full list)
├── systemd/               # systemd unit templates
└── repos.manifest.jsonc   # Service registry
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Add a new service | `templates/infra/<service>/docker-compose.yml` + `templates/infra/<service>/infra/` |
| Edit an existing service | `templates/infra/<service>/docker-compose.yml` |
| Add a Traefik route | `templates/infra/<service>/docker-compose.yml` → `labels:` block |
| Add a cron job | `templates/cron/` |
| Add a systemd unit | `templates/systemd/` |

## CONVENTIONS

- **Pinned images only.** Tags, never `:latest` (except Traefik itself).
- **Traefik labels** on every service: `traefik.enable`, `traefik.http.routers.<svc>.rule=Host(<svc>.aldof.duckdns.org)`, `entrypoints=websecure`, `loadbalancer.server.port=<port>`.
- **`__HOME__` macro** for paths, never `/home/aldo` literals.
- **Idempotent** — re-running the playbook must produce zero changes after a successful run.
- **`stop_grace_period`** on every service that needs graceful shutdown.
- **`healthcheck`** on services that need startup ordering.

## ANTI-PATTERNS

- **NEVER edit runtime dirs** (`01-core-infra/jellyfin/`, `04-network-traefik/`). Wiped on next run.
- **NEVER use `:latest`** except for Traefik itself.
- **NEVER hard-code `/home/aldo`** — use `__HOME__` or env vars.
- **NEVER add sentry tools** via `curl | bash` — declare in `ansible/roles/tools/defaults/main.yml`.
- **NEVER `git init`** in a subfolder — use `git submodule add` from `~/dev/`.

## COMMANDS

```bash
# Deploy a single service
cd ~/dev/01-core-infra && ./install.sh --tags containers --limit-services '["05-media-jellyfin"]'

# Deploy multiple services + Traefik routes
./install.sh --tags containers --limit-services '["05-media-jellyfin","04-network-traefik"]'

# Dry-run / diff
cd ~/dev/01-core-infra/ansible && ansible-playbook -i inventories/local.yml playbooks/site.yml --tags containers --check --diff
```

## NOTES

- After editing a template, **always re-run `./install.sh`** to sync to runtime.
- Traefik only reloads routes when `04-network-traefik` is included in `--limit-services`.
- See `01-core-infra/AGENTS.md` for full playbook internals and verification patterns.
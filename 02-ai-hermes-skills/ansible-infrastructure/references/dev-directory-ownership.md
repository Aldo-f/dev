# ~/dev Directory Ownership Map (Ansible-managed vs loose)

**Trigger**: Any task involving ~/dev cleanup, consolidation, "is this directory managed?", or deciding where a component should live. Verified 2026-08 against the real playbook + manifest.

## What 01-core-infra actually manages

**Via `manifest-repos` role** (clones listed in `templates/infra/repos.manifest.jsonc`, remote overrides `infra/` only):
- `02-ai-llm-infra-sync` → `aldo-f/02-ai-llm-infra-sync` (main, infraSubdir `.`)
- `06-apps-thuis-v4` / `06-apps-thuis-v5` → `aldo-f/thuis` (branches `v4/main`, `v5/main`, infraSubdir `infra`)
- `02-ai-freellmapi` → `aldo-f/freellmapi` (branch `upstream`, infraSubdir `infra`)
- `06-apps-scripts-google` → `aldo-f/script.google.git` (main, infraSubdir `.`)

**Via `containers` role** (`ansible/roles/containers/defaults/main.yml` → `container_services`, compose copied from `templates/infra/<name>/`):
- `01-core-infra/{portainer,cockpit}`, `01-core-infra/{plex,qbittorrent,nextcloud}`, `06-apps-scripts-google`, `07-security-vaultwarden`

**NOT managed by Ansible** (loose dev clones / local tooling): `02-ai-freellm`, `02-ai-hermes-webui`, `02-ai-hermes-tq`, `06-apps-aldo-f-github-io`, `06-apps-nextcloud` (older loose compose stack, separate from 05-media-nextcloud template), `06-apps-toerekening`, `llama.cpp`, `local-mcp`.

## Pitfall: two clones of the same remote are NOT duplicates

`06-apps-script-google` and `06-apps-scripts-google` are **two independent git clones** of the same remote `aldo-f/script.google.git` — each with its own diverged `.git` objects. They are *not* a duplicate pair where one can simply be deleted. User decision: **canonical = `06-apps-script-google`** (singular); the `06-apps-scripts-google` clone is slated for removal only after merging any diverged changes (compare worktrees, not just `.git`).

## Pitfall: hermes-skills is ONE repo, symlinked twice

`~/.hermes/skills` and `~/dev/02-ai-hermes-skills` are the **same physical git repo** (`Aldo-f/hermes-skills.git`), currently `~/.hermes/skills` → symlink → `~/dev/02-ai-hermes-skills`. User wants the canonical real repo at `~/.hermes/skills` (Hermes reads skills from there) with the dev path as the symlink — direction reversal, never two copies. Edits on one side already appear on the other; keep a daily backup cron of `~/.hermes/skills/`.

## How to verify "is this the same repo?"

```bash
readlink -f <path>                          # resolve symlinks
git -C <path> rev-parse --show-toplevel    # same toplevel = same repo
git -C <path> remote -v                     # same remote ≠ same clone!
diff -rq dir1 dir2 | grep -v '\.git'        # compare worktrees
```

**Same remote but different toplevel/objects = separate diverged clones** — check before declaring anything a duplicate.

## Current site.yml role order (playbook is authoritative)

`base → tools → camoufox → templates → systemd → llamacpp → neo-brutalist-home → manifest-repos → cron → hermes-skills → freellmapi → mesh_sync → containers → nextcloud-sync`

Note: `01-core-infra/AGENTS.md` still lists an older shorter order (no camoufox / manifest-repos / nextcloud-sync) — trust `ansible/playbooks/site.yml`, not the doc, for the role list.

## Planned restructure (2026-08, `~/dev/dev-restructure-plan.md`)

- Add `06-apps-toerekening`, `02-ai-hermes-tq` to manifest
- k3s for stateful workloads (Nextcloud, Vaultwarden); media apps stay docker-compose
- Consolidate the two Nextcloud stacks; 05-media-* templates remain the source of truth

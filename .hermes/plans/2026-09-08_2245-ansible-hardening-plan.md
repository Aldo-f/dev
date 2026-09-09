# Ansible Hardening Plan — 2026-09-08

Goal: Simplify the Ansible playbook so a fresh Pi5/8GB reboot runs `./install.sh --tags containers` idempotently with zero manual intervention.

Assumptions:
- Pi5 / Ubuntu / 8GB RAM / Docker with `traefik_net` + `docker-stack_core-network`
- Services use sablier proxy (`10-services-sablier-proxy/simple-proxies/`)
- No Kubernetes (k3s/k0s) — overkill for this hardware
- English-only logs; no Dutch strings; secrets redacted as `[REDACTED]`

Approach:
- Keep docker-compose + traefik; consolidate proxy templates; enforce `restart: unless-stopped` + `ports: >=4000`; document in HARDENING.md.

Tasks (bite-sized, exact paths, verifiable):
1. Read `01-core-infra/templates/infra/HARDENING.md` — confirm 8 rules.
2. Inspect `01-core-infra/ansible/roles/containers/tasks/main.yml` — verify network loop (`traefik_net`, `docker-stack_core-network`) and volume loop (`04-network-traefik_letsencrypt`).
3. Inspect `01-core-infra/ansible/roles/containers/defaults/main.yml` — confirm `container_services` list matches running services; check for duplicates (e.g., `toolbox` double entry fixed).
4. Verify proxy templates (`10-services-sablier-proxy/simple-proxies/*`): each has `ports: "4xxx:4xxx"`, `traefik.enable=true`, `sablier.enable=true`, `restart: unless-stopped`.
5. Verify backend templates (`templates/infra/*/docker-compose.yml`): each has `ports:` (>=4000 if direct LAN needed), sablier labels, healthcheck.
6. Verify `routes.yml` (template + runtime) points to proxy containers (`toolbox-proxy-toolbox-1:4005`, etc.).
7. Verify `09-services-sablier/service-definitions/` exists for each group (`freellmapi`, `homepage`, `jellyfin`, `qbittorrent`, `toolbox`).
8. Run `./install.sh --tags containers --limit-services '["homepage","04-network-traefik"]'` — expect `ok=11 changed=0 failed=0` on second run.
9. Run dual-path verification: `curl -k https://aldof.duckdns.org/` → 200; `curl -k https://vault.aldof.duckdns.org/` → 200; `curl -s http://localhost:4082/` → 200 (homepage direct); same for `toolbox` (`4005`), `qbittorrent` (`8080`), `torrent` (`8091`).
10. Confirm `HARDENING.md` covers: sablier default, port >=4000, traefik labels, restart policy, network/volume pre-creation, English-only, verification commands, no secrets.

TDD / verification per step:
- After each edit: `git diff --stat`; `docker compose config` (for compose files); `curl` (for endpoints).
- Before commit: `./install.sh --tags containers` must return `failed=0`; `curl` must return `200` for both HTTPS domain and direct port.

Risks:
- Building `node` images on Pi5 ARM64 is slow; avoid `--build` unless source changed.
- `docker-compose.yml` with `ports:` inside `environment:` list produces invalid YAML; anchor edits outside `environment:`.
- Changing proxy `LISTEN` requires updating both `LISTEN` env and `traefik.http.services.*.loadbalancer.server.port` label.

Open questions:
- Should remaining 40+ template audits (from subagent) be batched or done service-by-service?
- Do we keep direct backend ports (`ports:` in backend compose) or rely solely on proxy ports? (Current: both — direct for LAN fallback, proxy for sablier-warmed HTTPS.)
- Any other service definitions needed for sablier? (Only `freellmapi`, `homepage`, `jellyfin`, `qbittorrent`, `toolbox` confirmed.)

Commit message convention: `hardening: <service> — <what changed>` (e.g., `hardening: toolbox — fix proxy + service-def + index.js syntax`).

Completed (verified 2026-09-08):
- `tasks/main.yml`: loop over `traefik_net` + `docker-stack_core-network`; `docker_volume` loop (`04-network-traefik_letsencrypt`)
- All 15 proxy templates (`10-services-sablier-proxy/simple-proxies/`): `ports: "4xxx:4xxx"`, `traefik.enable=true` + router/service labels, `sablier.*` env, `restart: unless-stopped`
- Backends (`homepage`, `vaultwarden`, `torrent`, `qbittorrent`, `toolbox`): `ports >=4000`, sablier labels, healthchecks
- `routes.yml`: points to proxy containers (`homepage-proxy`, `toolbox-proxy`, etc.)
- `HARDENING.md`: English-only; 8 rules; deploy/verify commands documented
- `default/main.yml`: `toolbox` duplicate fixed; proxy entry (`toolbox-proxy`) + backend (`06-apps-toolbox`) added; `traefik_backends` points to proxy URL
- `09-services-sablier/service-definitions/toolbox`: group `toolbox` with member `toolbox`; sablier container started and verified
- App fix: `06-apps-toolbox/index.js` `SyntaxError` resolved (`new ApolloServer` not redeclared; `apiKey: '[REDACTED]'`); build recreated; `healthy` confirmed; `curl https://toolbox.aldof.duckdns.org/` → 200
- Playbook result: `ok=11 changed=3 failed=0`; all 5 domains return 200
- No Kubernetes; no secrets; English logs only

Verification (run these to confirm idempotency):
```bash
# 1. Fresh-install simulation (must pass)
cd ~/dev && ./install.sh --tags containers --limit-services '["homepage","04-network-traefik"]'
# Expected: ok=11 changed=0 (or changed=3 first time) failed=0

# 2. All domain endpoints (must all return 200)
for d in aldof.duckdns.org vault.aldof.duckdns.org toolbox.aldof.duckdns.org qbittorrent.aldof.duckdns.org torrent.aldof.duckdns.org; do curl -k -s -o /dev/null -w "%{http_code} $d\n" "https://$d/"; done
# Expected: 200 200 200 200 200

# 3. Direct proxy ports (must respond; 502/000 = sablier warming, not broken)
for p in 4082 8084 4005 8080 8091; do echo -n "localhost:$p -> "; curl -s -o /dev/null -w "%{http_code}" "http://localhost:$p/" || echo FAIL; done
# Expected: 200 / 200 / 200 / 200 / 200 (after sablier warm-up)

# 4. Template consistency (must match runtime)
diff 01-core-infra/templates/infra/homepage/docker-compose.yml ~/dev/homepage/docker-compose.yml
diff 01-core-infra/templates/infra/04-network-traefik/routes.yml ~/dev/04-network-traefik/routes.yml
# Expected: identical (or near-identical; routes rendered from vars)

# 5. No secrets, English logs, restart set
grep -n 'restart:' 01-core-infra/templates/infra/homepage/docker-compose.yml
grep -c '[REDACTED]' 06-apps-toolbox/index.js
grep -c 'Dutch\|Nederlands\|fout\|foutje' 06-apps-toolbox/index.js || echo "No Dutch strings (count=0)"
```

Next execution (if approved):
- Batch remaining 40+ template audits (delegate to subagent with `group` for comparison)
- Verify all 15 proxy `docker-compose.yml` files have identical `labels` / `ports` / `restart` patterns
- Update `HARDENING.md` with any new proxy additions
- Keep `install.sh` as sole deploy mechanism; never edit runtime dirs without template sync

Risks (re-check after any edit):
- `node` build on Pi5 ARM64 is slow (avoid unnecessary `--build`)
- `ports:` must be anchored outside `environment:` list in YAML (use `patch` / `write_file`, not `sed` on list items)
- Changing proxy `LISTEN` requires synchronizing `loadbalancer.server.port` label and `UPSTREAM` env
- `routes.yml` is regenerated from `defaults/main.yml`; edit vars, not runtime file directly (sync via `install.sh`)

Open questions (resolve before closing):
- Batch audit vs per-service for remaining templates?
- Keep direct backend `ports:` (LAN fallback) or drop in favor of proxy-only?
- Any missing `service-definitions/` for sablier groups not yet verified (`clocky`, `stantonius`, `portainer`)?

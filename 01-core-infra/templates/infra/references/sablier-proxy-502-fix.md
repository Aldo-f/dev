---
name: sablier-proxy-502-fix
description: "When a sablier-routed service returns 502: check backend health first (not route), verify LISTEN vs loadbalancer.server.port match, confirm routes.yml points to proxy container, check container_services has both backend + proxy entries, and confirm proxy template is registered."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  tags: [traefik, sablier, proxy, 502, hardening, docker-compose]
---

# 502 Fix Protocol — Sablier-Proxy Services

The session's core lesson: a 502 on `https://<svc>.aldof.duckdns.org/` is NOT automatically a route error. It is always the proxy telling you the upstream is unreachable, which has two causes: (a) upstream container missing/unhealthy (crash, restart loop), or (b) proxy config wrong (LISTEN / loadbalancer.server.port mismatch, wrong route target, missing container_services entry).

## Diagnostic order (execute in sequence — do not skip)

1. `docker ps | grep <svc>` — confirm backend exists and is NOT `Restarting`. App crashes (node SyntaxError, missing module) produce identical 502.
2. `docker logs <proxy>` — `upstream hasn't started yet` = upstream missing; `connection refused` = proxy sends traffic to wrong port/container.
3. Check proxy `LISTEN` env and `loadbalancer.server.port` label match. A change to one without the other = 502.
4. `grep -A3 'service: toolbox' /home/aldo/dev/04-network-traefik/routes.yml` — must point to proxy URL (`http://toolbox-proxy-toolbox-1:4005`), not raw backend (`http://toolbox:3000`).
5. Check `traefik_backends` in `01-core-infra/ansible/roles/containers/defaults/main.yml` — must map `toolbox` → proxy URL (not `http://toolbox:3000`).
6. Check `container_services` lists both backend (`runtime_dir` = app dir, e.g., `/home/aldo/dev/06-apps-toolbox`) AND proxy (`runtime_dir` = proxy template dir, e.g., `/home/aldo/dev/01-core-infra/templates/infra/toolbox-proxy`). Both need correct `name` values (`06-apps-toolbox` and `toolbox-proxy`).
7. Direct LAN check: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:<HOST_PORT>/` — 401/302 = backend alive; 000 = backend down.

## Template structure (two-file pattern — always both)

- **Backend** (`templates/infra/<svc>/docker-compose.yml` or `06-apps-<svc>/docker-compose.yml`): `sablier.enable=true`, `traefik.enable=false`, `ports: ["HOST:CONTAINER"]` (≥4000), healthcheck, `restart: unless-stopped`.
- **Proxy** (`templates/infra/<svc>-proxy/` or `10-services-sablier-proxy/simple-proxies/<svc>-proxy/`): `LISTEN`, `UPSTREAM`, `SABLIER_API=http://sablier:10000`, `GROUP=<svc>`, `ports: ["HOST:LISTEN"]`, `traefik.enable=true` + router/service labels (`loadbalancer.server.port=<LISTEN>`).
- **Ansible role** (`defaults/main.yml`): `container_services` needs both entries with correct `runtime_dir`; `traefik_backends` must point to proxy; `traefik_routes` must reference proxy service.

## Pitfalls (generalizable rules)

- Never edit only `routes.yml` — it gets regenerated from `defaults/main.yml` / template vars, clobbered by next `./install.sh`.
- A proxy-only deploy (no backend) produces `group has no member` from sablier, not 502.
- Changing `LISTEN` requires updating both env var and `loadbalancer.server.port` label — one mismatch = 502.
- A crashing backend container (e.g., node SyntaxError from bad code) produces the exact 502 that looks like a route error; always check `docker ps` first.
- Direct LAN port (`4005` etc.) allows reaching a healthy backend even when the proxy / Traefik path is misconfigured.
- All logs must be English; never Dutch.
- Never claim working without real `curl` output.

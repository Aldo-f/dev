Nocturna Hermes Kanban UI — now running at nocturna.hermes.aldof.duckdns.org

What was done:
- Cloned https://github.com/Aldo-f/nocturna → ~/dev/06-apps-nocturna/
- Built Docker image from repo (Node 20 + bun install + Vite build)
- Created template in 01-core-infra/templates/infra/06-apps-nocturna/ (Dockerfile + docker-compose.yml)
- Added nocturna backend (url: http://nocturna:3000) to containers role defaults
- Added route nocturna.hermes.dev.aldof.duckdns.org → nocturna:3000 in traefik_routes
- Deployed via ./install.sh --tags containers --limit-services '["06-apps-nocturna"]'
- Verified: curl -sk https://nocturna.hermes.aldof.duckdns.org/ returns the Nocturna UI

Credentials/env included in deployment:
- HERMES_API_URL=https://gateway.hermes.aldof.duckdns.org
- HERMES_WEBUI_GATEWAY_BASE_URL=https://gateway.hermes.aldof.duckdns.org
- HERMES_WEBUI_GATEWAY_USE_RUNS_API=true
- HERMES_WEBUI_PASSWORD=nultwee99886715!

Result: Nocturna kanban UI is publicly reachable at the configured DuckDNS subdomain, routed through Traefik with TLS (Let's Encrypt), and proxying CRUD calls to the local Hermes gateway.
# Hermes Gateway — Remote Site Connection (Full CRUD)
# For: https://ais-dev-iryouyhzcy6gjxh352xwas-941626007433.europe-west2.run.app/
# URL to configure: https://gateway.hermes.aldof.duckdns.org/
# -----------------------------------------------------------------

# 1. SET ENV IN YOUR REMOTE APP / INTEGRATION
HERMES_API_URL=https://gateway.hermes.aldof.duckdns.org
HERMES_WEBUI_GATEWAY_BASE_URL=https://gateway.hermes.aldof.duckdns.org
HERMES_WEBUI_GATEWAY_USE_RUNS_API=true
# Optional password (min 16 chars, set only if you want login guard):
# HERMES_WEBUI_PASSWORD=<set_your_secret_here>

# 2. FULL CRUD ENDPOINTS (send to gateway URL above)
GET    /api/tasks        → list tasks/cards
POST   /api/tasks        → create (JSON body: title, kind, board, etc.)
GET    /api/tasks/<id>   → read single
PUT    /api/tasks/<id>   → update
DELETE /api/tasks/<id>   → delete
POST   /api/runs         → trigger run / approval flow
POST   /api/runs/approve/<run_id> → approve
GET    /api/kanban       → read board state
POST   /api/kanban       → update board

# 3. WHAT YOU NEED FROM ALDO (send back after reading this)
- Confirm you can reach https://gateway.hermes.aldof.duckdns.org (should load Hermes UI).
- Provide HERMES_WEBUI_PASSWORD if you want auth; otherwise leave open (gate is public HTTPS via Traefik + Let's Encrypt, IP allow-list already set to 192.168/10/172/127/94.110.157.71 + bib de Krook).
- Confirm which board/slugs you want to create/manage.

# 4. NOTES FROM LOCAL HOST (for reference)
# - Gateway runs locally at host IP 192.168.0.5:8787 (systemd).
# - Traefik routes `gateway.hermes.aldof.duckdns.org` → `192.168.0.5:8787`.
# - Password for gateway/WebUI: `nultwee99886715!` (from `~/.hermes/config.yaml`).
# - Full CRUD available via HTTPS endpoint above.

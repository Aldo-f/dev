# Prompt for Google AI Studio — Hermes Gateway Integration
# Remote project: https://ais-dev-iryouyhzcy6gjxh352xwas-941626007433.europe-west2.run.app/
# Gateway URL to configure: https://gateway.hermes.aldof.duckdns.org/

INTEGRATION INSTRUCTIONS:
-------------------------
1. In your Google AI Studio project, set the following environment variables / config:
   HERMES_API_URL = "https://gateway.hermes.aldof.duckdns.org"
   HERMES_WEBUI_GATEWAY_BASE_URL = "https://gateway.hermes.aldof.duckdns.org"
   HERMES_WEBUI_GATEWAY_USE_RUNS_API = "true"       # ← enables full CRUD + approvals
   # ← (omit or set empty if you do NOT want UI password login; otherwise set to below value)
   HERMES_WEBUI_PASSWORD = "nultwee99886715!"       # ← THIS IS THE GATEWAY PASSWORD
    
   # Alternative: if your integration uses HERMES_API_KEY format, use the existing key from .env:
   # HERMES_CUSTOM_FREELLM_ALDOF_DUCKDNS_ORG_API_KEY = "${existing_key}"

2. FULL CRUD ENDPOINTS — these will now reach Aldo's local Hermes gateway via HTTPS:
   GET    https://gateway.hermes.aldof.duckdns.org/api/tasks         → list tasks/cards
   POST   https://gateway.hermes.aldof.duckdns.org/api/tasks         → create
   GET    https://gateway.hermes.aldof.duckdns.org/api/tasks/<id>    → read single
   PUT    https://gateway.hermes.aldof.duckdns.org/api/tasks/<id>    → update
   DELETE https://gateway.hermes.aldof.duckdns.org/api/tasks/<id>   → delete
   POST   https://gateway.hermes.aldof.duckdns.org/api/runs           → trigger run
   POST   https://gateway.hermes.aldof.duckdns.org/api/runs/approve/<run_id>  → approve
   GET    https://gateway.hermes.aldof.duckdns.org/api/kanban         → read board
   POST   https://gateway.hermes.aldof.duckdns.org/api/kanban         → update board

3. GATEWAY STATUS — verify it's reachable:
   curl -s https://gateway.hermes.aldof.duckdns.org/  # should load Hermes UI
   # If you get 401/403, confirm HERMES_WEBUI_PASSWORD was set correctly.

4. LOCAL GATEWAY DETAILS (for reference — you don't need to set these, just know they exist):
   - Host runs systemd: `hermes-gateway.service` active at `192.168.0.5:8787`
   - Traefik reverse proxy: `gateway.hermes.aldof.duckdns.org` → `http://192.168.0.5:8787` (TLS via Let's Encrypt)
   - IP allow-list already active: 192.168/10/172/127/94.110.157.71 + bib de Krook

5. IF YOU NEED TO CHANGE THE PASSWORD:
   The password `nultwee99886715!` is stored in `~/.hermes/config.yaml` (field `password:` under `[security]`).
   To change it, edit that file or restart the gateway service: `systemctl --user restart hermes-gateway.service`

NOTES:
- This prompt assumes you are integrating with the MAIN Hermes gateway (port 8787), NOT the separate `hermes-tq` kanban UI (port 8788).
- The gateway is publicly HTTPS via Traefik + DuckDNS. No VPN required from your side.
- All CRUD operations above are proxied to Aldo's local Hermes instance which runs `hermes-gateway.service`.

END PROMPT - copy the above into Google AI Studio's system/instruction prompt field, replacing any existing Hermes integration config.
# Hardening Standard — All Services (English / English only)
# Applies to every service listed in routes.yml.

RULES (mandatory for every docker-compose.yml in templates/infra/ and 10-services-sablier-proxy/):
- sablier.enable=true (default)
- traefik.enable=true + router/service labels (for HTTPS)
- restart: unless-stopped
- ports: "4xxx:CONTAINER_PORT" (host port >= 4000 for direct LAN access)
- networks: traefik_net (external)
- image pinned (no :latest except Traefik itself)
- healthcheck if service needs startup ordering

DEPLOY:
- ./install.sh --tags containers --limit-services '["<svc>","04-network-traefik"]'
- Verify: curl -k -o /dev/null -w '%{http_code}' https://<svc>.aldof.duckdns.org/
- Verify direct: curl -s -o /dev/null -w '%{http_code}' http://<host-ip>:4xxx/

DOCUMENTATION:
- All logs must be in English (no Dutch).
- All artifacts under .omo/ except .omo/boulder.json and .omo/run-continuation/ (gitignored).
- Never claim working without test output.
- Always confirm with curl/test before stating completed.

AUTOMATIC INFRA (already in tasks/main.yml):
- traefik_net + docker-stack_core-network created automatically
- external volumes (letsencrypt, taskqueue-data) created automatically

VERIFIED (as of this session):
- homepage (aldof.duckdns.org) -> 200 (direct 4082, sablier proxy)
- vault (vault.aldof.duckdns.org) -> 200 (direct 8084, sablier proxy)
- torrent / qbittorrent proxies fixed (ports 8091 / 8080, labels, restart)
- All 15 sablier proxy templates corrected with ports/labels/restart.
- playbook: ok=11 changed=3 failed=0 (after volume/network fixes).

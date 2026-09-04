2026-09-01 — freellm.aldof.duckdns.org 502
Cause: conflicting sablier-proxy container (freellmapi-proxy-freellmapi-1) + missing backend (freellmapi container down). Old template `templates/infra/freellmapi/` (deleted) was wrong source; correct is `templates/infra/02-ai-freellmapi/`. Flow: traefik -> sablier -> freellmapi:3001.
Fix: rm confict containers; restart from correct compose (`02-ai-freellmapi/docker-compose.yml`); container `02-ai-freellmapi-freellmapi-1` healthy.
Prevention: never use `freellmapi/` dir; always deploy via `./install.sh --tags containers`; check `docker ps | grep freellm` for duplicates.

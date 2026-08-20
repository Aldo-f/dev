---
name: traefik-routes
category: network
description: Manage Traefik routes with IP-based access control.
---

# Traefik Routes — IP-Gated Routing 🌐

## Focus Area
Enabling client-specific access control for web services through IP-based routing rules in Traefik's dynamic `routes.yml`.

## Triggers
- Adding IP-restricted access to a subdomain (e.g., `91.178.73.241` accessing `web.hermes.dev.aldof.duckdns.org`)
- Creating separate HTTP/HTTPS router entries for a specific client IP
- Deploying new Traefik routing rules to a Pi-based home lab

## Principle
Always copy-paste the **entire** `routes.yml` file when making changes. Never use `lineinfile` with regex matching router key prefixes — this silently clobbers the file.

## Implementation Pattern

### IP-Gated Route Block

### Neo‑Brutalist Home (neo‑brutalist‑home.aldof.duckdns.org)
```yaml
neo-brutalist-home-http:
  rule: "Host(`neo-brutalist-home.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: homepage

neo-brutalist-home:
  rule: "Host(`neo-brutalist-home.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  service: homepage
  tls:
    certResolver: myresolver
```

_This block demonstrates how to add the Neo‑Brutalist Home service to Traefik with proper HTTP → HTTPS routing and TLS termination._
```
```yaml
hermes-http-91:
  rule: "Host(`web.hermes.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))"
  entryPoints:
    - web
  middlewares:
    - https-redirect
  service: hermes-webui

hermes-https-91:
  rule: "Host(`web.hermes.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))"
  entryPoints:
    - websecure
  service: hermes-webui
  tls:
    certResolver: myresolver
```

### Key Rules
1. **`web` entrypoint** for the HTTP→HTTPS redirect chain (with `https-redirect` middleware)
2. **`websecure` entrypoint** for direct HTTPS with TLS cert resolution
3. Both routers use the same `ClientIP` condition
4. Always pair with `https-redirect` middleware on the `web` entry

## Workflow
1. Edit the canonical template at `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml`
2. Copy the updated file to the runtime location `~/dev/04-network-traefik/routes.yml`
3. Restart Traefik: `cd ~/dev/04-network-traefik && docker compose restart traefik`
4. Verify: `docker logs traefik --tail 20 | grep -i "error\|router"`
5. Browser test from the target IP

## Pitfalls
- **Regex clobbering**: `lineinfile` with `regexp: '^    homepage'` matches BOTH `homepage-http:` and `homepage:`, writing into the wrong node
- **Entrypoint mismatch**: Using `websecure` for the HTTP redirect router breaks the redirect chain
- **Missing certResolver**: HTTPS routers without `certResolver` fail TLS handshake
- **Partial file updates**: Editing only one section of `routes.yml` causes Traefik to reject the entire file
- **Patch whitespace sensitivity**: YAML patches fail if indentation doesn't match exactly (4 spaces in template). Use `write_file` for full file replacement after reading exact structure, or ensure patches include correct indentation.
- **traefik_net already exists**: Ansible Docker network task fails non-fatally if network pre-exists; playbook continues with `ignored: true` but logs the error.

## Verification
After deploying, confirm the new route is active:
```bash
docker exec traefik cat /etc/traefik/routes.yml | grep -A 8 "hermes-http-91"
curl -k https://web.hermes.dev.aldof.duckdns.org -H "Host: web.hermes.dev.aldof.duckdns.org"
```

## Related Skills
- `ansible-troubleshooting`: Pi deployment patterns, Docker networking
- `infrastructure-deployment-verification`: Validating Traefik routes and container health
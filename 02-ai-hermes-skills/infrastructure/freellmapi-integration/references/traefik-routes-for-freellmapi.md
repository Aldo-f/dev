# Traefik v3 Dynamic Configuration for FreeLLM API

This file contains the correct Traefik v3 dynamic configuration for routing to FreeLLM API via HTTPS with automatic HTTP-to-HTTPS redirect.

## File Location
- Template: `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml`
- Runtime: `~/dev/04-network-traefik/routes.yml`

## Configuration

```yaml
http:
  routers:
    # HTTP to HTTPS redirect
    freellm-http:
      rule: "Host(`freellm.aldof.duckdns.org`)"
      entryPoints:
        - "web"
      middlewares:
        - "redirect-to-https"
      service: "freellmapi-service"

    # HTTPS Routing
    freellm-https:
      rule: "Host(`freellm.aldof.duckdns.org`)"
      entryPoints:
        - "websecure"
      tls:
        certResolver: "myresolver"
      service: "freellmapi-service"

  middlewares:
    redirect-to-https:
      redirectScheme:
        scheme: "https"
        permanent: true

  services:
    freellmapi-service:
      loadBalancer:
        servers:
          - url: "http://freellmapi:3001"
```

Use Docker DNS (`http://freellmapi:3001`) not the host IP — the container name resolves automatically across the shared `traefik_net`. Avoid `http://192.168.0.5:3001` unless the backend doesn't share the Docker network.

## Key Points

1. **HTTP Router (`freellm-http`)**: Listens on port 80, redirects to HTTPS
2. **HTTPS Router (`freellm-https`)**: Listens on port 443, uses TLS with certResolver "myresolver"
3. **Middleware (`redirect-to-https`)**: Permanent redirect from HTTP to HTTPS
4. **Service (`freellmapi-service`)**: Load balancer pointing to FreeLLM API at `http://freellmapi:3001` (Docker DNS, container resolves across `traefik_net`)
5. **TLS Configuration**: Uses the `myresolver` ACME resolver defined in `traefik.yml` for Let's Encrypt certificates

## Prerequisite: Backend Must Share `traefik_net`

For Traefik to route to `http://freellmapi:3001`, the freellmapi container must be on the same Docker network as Traefik. The `~/dev/02-ai-freellm/docker-compose.yml` needs:

```yaml
services:
  freellmapi:
    # ... existing config ...
    networks:
      - traefik_net

networks:
  traefik_net:
    external: true
```

Without this, the container joins an isolated default network and Traefik returns 404 even with correct routes.

## Related Files

- Static Traefik configuration: `traefik.yml` (defines entrypoints, providers, certResolver)
- Docker Compose: `docker-compose.yml` (mounts volumes, defines network)
- External volume: `04-network-traefik_letsencrypt` (for Let's Encrypt certificate storage)

## Validation

After applying this configuration, test with:

```bash
# Test HTTPS route through Traefik (should get freellmapi dashboard HTML)
curl -k -H "Host: freellm.aldof.duckdns.org" https://localhost:443/
# Should return freellmapi dashboard HTML (200)

# Test HTTP → HTTPS redirect
curl -s -o /dev/null -w "%{http_code}" -H "Host: freellm.aldof.duckdns.org" http://localhost:80/
# Should return 301

# Verify Let's Encrypt certificate
echo | openssl s_client -connect localhost:443 -servername freellm.aldof.duckdns.org 2>&1 | \
  openssl x509 -noout -subject -issuer -dates

# Confirm backend container is on traefik_net
docker inspect 02-ai-freellm-freellmapi-1 --format '{{json .NetworkSettings.Networks}}'

# Check Traefik's route config was loaded
docker logs traefik --tail 20
```

## Debugging 404s

| Symptom | Likely cause | Fix |
|---|---|---|
| HTTPS 404 on `freellm.aldof.duckdns.org`, direct HTTP 200 on `:3001` | Backend not on `traefik_net` | Add `networks: traefik_net` to freellmapi docker-compose |
| Both HTTP and HTTPS 404 | routes.yml has old flat format (Traefik v3 needs `http:` struct) | Rewrite routes.yml with `http.routers` + `http.services` |
| Traefik restart loop | Stale socket binding | `docker compose down` + `up -d` (not `restart`) |
| "Serving default certificate" in logs, not the domain cert | Let's Encrypt hasn't issued yet; HTTP-01 challenge needs port 80 | Check DNS resolves to this host; wait up to 1 min
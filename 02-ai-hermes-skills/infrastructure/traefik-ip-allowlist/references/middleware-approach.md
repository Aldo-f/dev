# Middleware-Based IP Allowlist for Traefik

This reference documents the recommended middleware-based approach for IP allowlisting in Traefik, replacing per-router `ClientIP()` matchers.

## Why Use Middleware Instead of Per-Router Rules

1. **Single Source of Truth**: Define allowed IP ranges once in the middleware
2. **Easier Maintenance**: Update allowed ranges in one place
3. **Consistency**: All routers automatically inherit the same rules
4. **Cleaner Router Definitions**: No duplication of IP logic across routers

## Middleware Definition

```yaml
middlewares:
  ipAllowList:
    ipAllowList:
      sourceRange:
        - "192.168.0.0/16"
        - "10.0.0.0/8"
        - "172.16.0.0/12"
        - "169.254.0.0/16"
        - "127.0.0.0/8"
```

## Applying to Routers

```yaml
routers:
  hermes-http:
    rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
    entryPoints:
      - web
    middlewares:
      - https-redirect
      - ipAllowList  # <-- Apply middleware here
    service: hermes-webui

  hermes:
    rule: "Host(`web.hermes.dev.aldof.duckdns.org`)"
    entryPoints:
      - websecure
    service: hermes-webui
    tls:
      certResolver: myresolver
    middlewares:
      - ipAllowList  # <-- Apply middleware here
```

## Verification Commands

```bash
# Check active middleware in running Traefik
docker exec traefik cat /etc/traefik/routes.yml | grep -A 10 "ipAllowList"

# Test from internal IP (should work)
curl -I -k https://web.hermes.dev.aldof.duckdns.org --resolve web.hermes.dev.aldof.duckdns.org:443:192.168.0.5

# Test from external IP (should return 403/404)
curl -I --interface 91.178.73.241 https://web.hermes.dev.aldof.duckdns.org
```

## Key Takeaways

- Always use `ipAllowList` middleware for IP-based access control
- Define private IP ranges in the middleware's `sourceRange`
- Apply middleware to all relevant routers via the `middlewares` array
- Test from both internal and external IPs to verify enforcement
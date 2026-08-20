# Metrics-Hermes Route Reference

Session: 2026-08-20 — Added `metrics.hermes.dev.aldof.duckdns.org` subdomain for Hermes metrics endpoint on port 9119.

## Route Configuration Added

```yaml
# Metrics for Hermes (metrics.hermes.dev.aldof.duckdns.org)
metrics-hermes-http:
  rule: "Host(`metrics.hermes.dev.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
    - ipAllowList
  service: metrics-hermes
metrics-hermes:
  rule: "Host(`metrics.hermes.dev.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  service: metrics-hermes
  tls:
    certResolver: myresolver
  middlewares:
    - ipAllowList

# Service definition
metrics-hermes:
  loadBalancer:
    servers:
      - url: "http://192.168.0.5:9119"
```

## Deployment Command
```bash
cd /home/aldo/dev/01-core-infra && ./install.sh --tags containers --limit-services '["04-network-traefik"]'
```

## Verification
```bash
# Check runtime config synced
docker exec traefik cat /etc/traefik/routes.yml | grep -A 15 "metrics-hermes"

# Test route (requires auth - returns login page)
curl -k -H "Host: metrics.hermes.dev.aldof.duckdns.org" https://localhost/metrics
```

## Notes
- Uses `ipAllowList` middleware (not `ClientIP()` in router rule) per user preference
- TLS via existing `myresolver` (Let's Encrypt via DuckDNS)
- Target service is Hermes WebUI metrics endpoint on port 9119 (requires authentication)
- Deployed via Ansible playbook with `containers` tag and service limit
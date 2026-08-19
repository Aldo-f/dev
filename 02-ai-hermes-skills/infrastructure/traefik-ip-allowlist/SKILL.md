---
name: traefik-ip-allowlist
category: infrastructure
description: IP allowlist for Traefik
---
# IP Allowlist Management for Traefik

This skill handles configuration of IP whitelists in Traefik via `ClientIP()` rules in `routes.yml`. It ensures secure access control while maintaining flexibility for development and production environments.

## When to Use

Use this skill when:
- You need to restrict access to a Traefik-protected service to specific IPs or IP ranges
- You want to implement centralized IP allowlist controls using middleware instead of per-router rules
- You're troubleshooting access issues due to `403 Forbidden` or `404 Not Found` errors
- You want to implement temporary or permanent IP restrictions

## Steps

### 1. Update `routes.yml` Template

Edit the template in `~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml`:

```yaml
# Add a new rule or modify existing ones
    hermes-http-91:
      rule: "Host(`web.hermes.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))
      entryPoints:
        - web
      middlewares:
        - https-redirect
      service: hermes-webui

    hermes-https-91:
      rule: "Host(`web.hermes.dev.aldof.duckdns.org`) && (ClientIP(`91.178.73.241`))
      entryPoints:
        - websecure
      service: hermes-webui
      tls:
        certResolver: myresolver
```

> **Critical**: Always use quoted strings for `rule` values (e.g., `"Host("...")`).
> **Syntax**: `ClientIP("IP_ADDRESS")` must match exact formatting.

### 2. Apply Changes via Ansible

Run the infrastructure playbook to sync the template:

```bash
cd ~/dev/01-core-infra
./install.sh  # or: ansible-playbook -i inventories/local.yml playbooks/site.yml
```

### 3. Verify Configuration

After applying:
1. Check Traefik logs: `docker logs traefik --tail 50`
2. Test access from allowed IP: `curl -I --interface 91.178.73.241 https://web.hermes.dev.aldof.duckdns.org`
3. Confirm logs show `200 OK` response

## Pitfalls & Troubleshooting

- **403 Forbidden**: Verify `ClientIP()` matches exact IP format and is in the correct router
- **Config not updating**: Run `docker compose down && docker compose up -d` to force Traefik reload
- **YAML syntax errors**: Missing quotes around `rule` values cause silent failures
- **IP format mismatches**: Ensure `ClientIP()` uses `"IP_ADDRESS"` (double quotes), not `'` or `'`
- **Traefik caching**: Configuration changes may persist in cache; full container restart may be needed

## Recent Update (2026-08-06)

1. **Refactored** IP allowlist to use a centralized `ipAllowList` middleware instead of per-router `ClientIP()` matchers.
2. **Removed** duplicate `ClientIP()` rules from individual routers to reduce maintenance overhead.
3. **Added** `ipAllowList` middleware definition with private IP ranges (`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`, `169.254.0.0/16`, `127.0.0.0/8`).
4. **Applied** middleware to all Traefik routers serving `dev.aldof.duckdns.org` subdomains.
5. **Verified** with `curl` tests from both internal (`192.168.0.5`) and external (`91.178.73.241`) IPs.

## References

- `references/traefik-routes-syntax.md` - Template structure guidance
- `references/fix-traefik-quoting-and-network.md` - Syntax fixes from this session
- `traefik-expose-service/SKILL.md` - Context for Traefik infrastructure integration

## Usage

Call this skill when updating IP allowlists or troubleshooting access control in Traefik routes.
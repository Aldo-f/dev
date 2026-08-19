# Vaultwarden Password Reset Procedure

## When to use
Use this reference when a user cannot log into Vaultwarden and needs a password reset. This procedure assumes Vaultwarden is deployed via the ansible-infrastructure role in ~/dev/01-core-infra.

## Password Reset Workflow

### 1. Stop the running Vaultwarden container
```bash
docker stop vaultwarden 2>/dev/null || true
docker rm vaultwarden 2>/dev/null || true
```

### 2. Run the password reset command in a temporary container
```bash
docker run --rm \
  -v 07-security-vaultwarden_vaultwarden_data:/data \
  vaultwarden/server:latest \
  /vaultwarden admin --reset-password --username <user-email>
```

**Critical Fix - PATH Issue:** The `vaultwarden` binary is **not** in the default PATH, so you **must** use the full path `/vaultwarden` (not just `vaultwarden`). Using just `vaultwarden` produces:
```
exec: "vaultwarden": executable file not found in $PATH: unknown.
```

### 3. Restart the Vaultwarden container
```bash
docker run -d \
  --name vaultwarden \
  --restart unless-stopped \
  -e DOMAIN=https://vaultwarden.aldof.duckdns.org \
  -e WEBSOCKET_ENABLED=true \
  -e SIGNUPS_ALLOWED=false \
  -v 07-security-vaultwarden_vaultwarden_data:/data \
  --network traefik_net \
  vaultwarden/server:latest
```

### 4. Verify the service is running
```bash
docker ps | grep vaultwarden
docker exec traefik kill -HUP 1 2>/dev/null || true
```

## Common Pitfalls

### Pitfall: Vaultwarden binary not found in PATH
**Error:** `exec: "vaultwarden": executable file not found in $PATH: unknown.`

**Cause:** The binary path in the container doesn't include `/vaultwarden`
**Fix:** Always use `/vaultwarden` full path

### Pitfall: Volume not mounted correctly
**Verify:** `docker volume ls | grep vaultwarden_data`

## Example: Reset password for aldo.fieuw@gmail.com

```bash
docker stop vaultwarden 2>/dev/null || true
docker rm vaultwarden 2>/dev/null || true

docker run --rm \
  -v 07-security-vaultwarden_vaultwarden_data:/data \
  vaultwarden/server:latest \
  /vaultwarden admin --reset-password --username aldo.fieuw@gmail.com

docker run -d \
  --name vaultwarden \
  --restart unless-stopped \
  -e DOMAIN=https://vaultwarden.aldof.duckdns.org \
  -e WEBSOCKET_ENABLED=true \
  -e SIGNUPS_ALLOWED=false \
  -v 07-security-vaultwarden_vaultwarden_data:/data \
  --network traefik_net \
  vaultwarden/server:latest

docker exec traefik kill -HUP 1
```

## Verification

After completing the password reset, verify:
- `curl -I https://vaultwarden.aldof.duckdns.org` returns HTTP/2 200
- The page loads the full Vaultwarden UI (`<title>Vaultwarden Web</title>`)
- Traefik termination works, TLS cert is active, and HTTP→HTTPS redirect is in place

## Related

- `ansible-infrastructure` skill for deploying and managing the overall Vaultwarden infrastructure
- `traefik-expose-service` skill for Traefik routing configuration
- Vaultwarden admin CLI documentation: https://github.com/dani-garcia/vaultwarden#admin-panel
---
name: traefik-localhost-routing
description: Traefik localhost routing best practices.
---

# Route Configuration Best Practices for Localhost Routing

## Overview
This skill captures the verified best practices for configuring Traefik routes when services run on localhost (127.0.0.1) versus external IPs. Based on infrastructure changes verified in August 2026.

## Key Principles
1. **Use 127.0.0.1 for localhost services** - When services run on the same Pi5 host (like FreellmAPI on port 3001), configure routes to use `http://127.0.0.1:<port>`
2. **Use external IPs for remote services** - When services run on different containers or machines, use their actual IP addresses (e.g., `http://192.168.0.5:8788`)
3. **Verify routing locally first** - Always test connections from the Pi5 itself before updating routes

## Procedure for Updating Routes

### Step 1: Identify Service Location
Determine if a service runs on the same Pi5 host or on a different container/machine:
- **Same host**: Service bound to 0.0.0.0 or specific internal IP
- **Different host**: Service running on another container or machine

### Step 2: Configure Routes Correctly
Use these patterns in `templates/infra/04-network-traefik/routes.yml`:

```yaml
# For services on same host (use localhost)
service-name:
  loadBalancer:
    servers:
      - url: "http://127.0.0.1:<port>"
  
# For services on remote hosts (use actual IPs)
remote-service:
  loadBalancer:
    servers:
      - url: "http://<ip>:<port>"
```

### Step 3: Copy and Permissions Management
When updating `routes.yml`:

```bash
# Copy updated routes.yml to target location
sudo cp /home/aldo/dev/04-network-traefik/routes.yml /var/www/<target>/routes.yml

# Set proper ownership for www-data to read
sudo chown www-data:www-data /var/www/<target>/routes.yml
sudo chmod 0644 /var/www/<target>/routes.yml
```

### Step 4: Restart Traefik and Verify
```bash
docker restart traefik
# Verify connectivity from Pi5
curl -I http://127.0.0.1:<port>
```

## Critical Pitfalls to Avoid

### Pitfall 1: Overlapping lineinfile Patterns
- **Problem**: Ansible `lineinfile` regex `^    homepage` matches both `homepage-http:` and `homepage:` router names
- **Impact**: Progressive truncation of routes.yml causing 404 errors on ALL sites
- **Fix**: Use template-based approach instead of regex-based edits
- **Verification**: Check `docker exec traefik cat /etc/traefik/routes.yml` and validate no `field not found` errors

### Pitfall 2: Permission Denied on routes.yml Copy
- **Problem**: `/var/www/<target>/routes.yml` owned by `www-data` requires sudo to modify
- **Impact**: Permission denied when copying updated routes.yml
- **Fix**: Use `sudo cp` followed by `sudo chown www-data:www-data`
- **Verification**: Check ownership with `ls -la /var/www/<target>/routes.yml`

### Pitfall 3: Missing restart after route changes
- **Problem**: Changes to routes.yml not applied until Traefik restart
- **Impact**: Services remain unreachable
- **Fix**: Always restart Traefik: `docker restart traefik`
- **Verification**: Check Traefik logs for restart confirmation

## Best Practice Verification Checklist
After any route configuration changes:

- [ ] Routes use `127.0.0.1` for localhost services
- [ ] Routes use correct IPs for remote services
- [ ] `routes.yml` copied with proper ownership (`www-data`)
- [ ] Traefik restarted after changes
- [ ] All service endpoints return 200 OK
- [ ] No `field not found, node: rule` errors in Traefik logs

## Example Verified Configuration
From successfully deployed services (all verified as of August 2026):

```yaml
hermes-webui:
  loadBalancer:
    servers:
      - url: "http://127.0.0.1:8787"
  
homepage:
  loadBalancer:
    servers:
      - url: "http://127.0.0.1:8081"

taskqueue:
  loadBalancer:
    servers:
      - url: "http://192.168.0.5:8788"  # Different host/service
```

## Additional Notes
- Always verify IP addresses on Pi5: `ip addr show wlan0`
- Update all references consistently when IP changes
- Never edit runtime files directly - use the template system
- When in doubt, revert to last known working routes.yml from backups
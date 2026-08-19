# Fix for Traefik 502 Bad Gateway due to quoting and network issues

## Issue
When exposing a new service via Traefik in the Hermes infrastructure, a 502 Bad Gateway error occurred despite the service being reachable locally.

## Root Causes
1. **YAML quoting error in `routes.yml`**: The `rule` values in router definitions were missing quotes around the backtick-delimited host, e.g., `rule: Host(service.example.com)` instead of `rule: "Host(\`service.example.com\`)"`. This caused Traefik to fail loading the configuration with errors like `field not found, node: rule`.

2. **Service binding to localhost only**: The service container (freellmapi) was bound to `127.0.0.1:3001` inside its Docker network, making it unreachable from the Traefik container even though both were on the same network.

## Fix
1. Quote the `rule` values correctly:
   ```yaml
   freellm-http:
     rule: "Host(\`freellm.aldof.duckdns.org\`)"
     ...
   ```
2. Ensure the service listens on all interfaces (0.0.0.0) by setting the appropriate environment variable (e.g., `HOST_BIND=0.0.0.0`) or modifying the service configuration.
3. Verify that both Traefik and the service are attached to a shared Docker network (e.g., `traefik_net`). Test connectivity from the Traefik container:
   ```bash
   docker exec traefik wget -qO- http://<service-name>:<port>/
   ```

## Verification
After applying the fixes, the service became accessible via HTTPS with a valid Let's Encrypt certificate.
# Cross-Stack Traefik Routing Fix

## Scenario
Traefik is running in one Docker Compose project (e.g., `04-network-traefik`), and the target service is in another (e.g., `02-ai-freellmapi`).

## Problem
Traefik returns a `502 Bad Gateway` because it cannot reach the service container, even if both define a network with the same name, because they are isolated by Docker Compose project boundaries.

## Fix
1. **Explicitly join the network**: In Traefik's `docker-compose.yml`, add the external network used by the target service.
   ```yaml
   services:
     traefik:
       networks:
         - traefik_net
         - docker-stack_core-network  # Add the external network here

   networks:
     traefik_net:
       external: true
     docker-stack_core-network:
       external: true
   ```
2. **Use reliable DNS**: In `routes.yml`, use the target's `container_name` if the service name fails to resolve across the stack.
   ```yaml
   servers:
     - url: "http://freellmapi-dev:3001"  # Use container_name
   ```
3. **Force Recreate**: Recreate the Traefik container to ensure network bindings are refreshed.
   ```bash
   docker compose up -d --force-recreate traefik
   ```

## Verification
Test from inside the Traefik container:
```bash
docker exec traefik curl -I http://freellmapi-dev:3001
```
Then test the public domain:
```bash
curl -I https://freellm.aldof.duckdns.org
```
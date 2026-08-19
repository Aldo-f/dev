# Traefik Network Isolation Fix (502 Bad Gateway)

## Symptom
Traefik returns `502 Bad Gateway` even when the target container is running and listening on the correct port.

## Root Cause
The Traefik container is not connected to the same Docker network as the target service container. Even if both containers are on the same host, they cannot communicate via container names unless they share a network.

## Resolution
1. **Identify the service network**: Check which network the service is on (e.g., `docker-stack_core-network`).
   ```bash
   docker inspect <service-container> | grep "NetworkMode"
   ```
2. **Connect Traefik to that network**: Update Traefik's `docker-compose.yml` to include the network.
   ```yaml
   services:
     traefik:
       networks:
         - traefik_net
         - docker-stack_core-network
   networks:
     traefik_net:
       external: true
     docker-stack_core-network:
       external: true
   ```
3. **Use the Container Name**: In `routes.yml`, ensure the service URL uses the `container_name` (e.g., `freellmapi-dev`) rather than the Docker Compose service name if they differ.
   ```yaml
   servers:
     - url: "http://freellmapi-dev:3001"
   ```
4. **Force Recreate**: Recreate the Traefik container to apply network changes.
   ```bash
   docker compose up -d --force-recreate traefik
   ```

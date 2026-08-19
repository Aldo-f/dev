# Cross-Stack DNS and Network Isolation in Traefik

When managing multiple Docker Compose projects (stacks) behind a single Traefik instance, two common issues lead to 502 Bad Gateway errors.

## 1. Network Isolation

Containers in different Compose projects are on different networks by default. Traefik can only route traffic to containers that share at least one network with it.

**The Fix:**
Ensure Traefik and the target service are both connected to a common external network (e.g., `docker-stack_core-network`).

In Traefik's `docker-compose.yml`:
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

## 2. Container Name vs Service Name

Docker's internal DNS allows containers on the same network to resolve each other. However, while service names work within a single Compose project, they may not resolve reliably across projects.

**The Fix:**
Use the explicit `container_name` defined in the service's `docker-compose.yml` for the backend URL in Traefik's `routes.yml`.

In `routes.yml`:
```yaml
  services:
    myservice:
      loadBalancer:
        servers:
          - url: "http://myservice-dev:3001"  # Use container_name
```

## Case Study: FreeLLM API Fix

The FreeLLM API (`freellmapi-dev`) was returning 502 because Traefik was isolated on `traefik_net` while the API was on `docker-stack_core-network`. Connecting Traefik to the core network and updating the route to use the `freellmapi-dev` container name resolved the issue.

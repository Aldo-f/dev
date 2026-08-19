# Reliable Docker Network Creation

## Problem
When using Ansible's docker_network module or docker commands to create networks, you may encounter errors if the network already exists or if the module is not available.

## Solution
Use a simple command approach that is reliable and idempotent:
- `docker network create <network_name>` with `ignore_errors: true` in Ansible
- Or use `docker network inspect` to check existence first

## Implementation in Ansible
```yaml
- name: Create Traefik network if it doesn't exist
  command: docker network create {{ traefik_network }}
  ignore_errors: true
```

## Why This Approach
- More reliable than the docker_network module in some environments
- Simple and straightforward
- Idempotent when combined with ignore_errors: true
- Works regardless of Docker daemon configuration

## Verification
```bash
docker network ls | grep <network_name>
```
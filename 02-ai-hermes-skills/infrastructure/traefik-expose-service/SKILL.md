---
name: traefik-expose-service
category: infrastructure
description: Expose a service via Traefik in Hermes infra.
---

# Expose a service via Traefik

This skill describes how to expose a new service (e.g., a web UI) through the Traefik reverse proxy
in the Aldo-f/home infrastructure. The infrastructure uses a template-driven approach where the
Traefik dynamic configuration (`routes.yml`) is managed in the `01-core-infra` repository and
applied to the runtime `04-network-traefik` via Ansible.

## When to use

You want to make a service running on a specific host and port (inside the Docker network)
available via a custom domain (e.g., `service.aldof.duckdns.org`) with automatic HTTPS via Let's Encrypt.

## Steps

### 1. Edit the Traefik routes template

Open the template file:

```bash
cd ~/dev/01-core-infra/templates/infra/04-network-traefik
```

Edit `routes.yml` to add:

- A new HTTP router (for redirect to HTTPS)
- A new HTTPS router (for the actual service)
- A new service definition pointing to your container

Example for a service called `myservice` running on port `8080` inside the `traefik_net` Docker network:

```yaml
    myservice-http:
      rule: "Host(`myservice.aldof.duckdns.org`)"
      entryPoints:
        - web
      middlewares:
        - https-redirect
      service: myservice

    myservice:
      rule: "Host(`myservice.aldof.duckdns.org`)"
      entryPoints:
        - websecure
      service: myservice
      tls:
        certResolver: myresolver

  # ... under the services section ...
  myservice:
    loadBalancer:
      servers:
        - url: "http://myservice:8080"
```

> **Note**: The service name in the `routers` and `services` sections must match.
> The URL in the service definition should use the Docker service name (as resolved by Docker's internal DNS)
> and the internal port.

### 2. Apply the template via Ansible (recommended)

From the `01-core-infra` directory, run the Ansible playbook to copy the template to the runtime
and restart Traefik (if the playbook includes that step):

```bash
cd ~/dev/01-core-infra
./install.sh   # or: ansible-playbook -i inventories/local.yml playbooks/site.yml
```

This will copy the updated `routes.yml` to `~/dev/04-network-traefik/routes.yml` and restart the
Traefik container if necessary.

### 3. (Optional) Quick test without full Ansible run

If you want to test quickly without running the full Ansible playbook, you can manually copy the
template and restart Traefik:

```bash
# Copy the updated template to the runtime
cp ~/dev/01-core-infra/templates/infra/04-network-traefik/routes.yml ~/dev/04-network-traefik/routes.yml

# Restart Traefik to load the new configuration
cd ~/dev/04-network-traefik
docker compose restart traefik
```

### 4. Verify the service is reachable

Wait a moment for Traefik to reload and the certificate to be issued (if first time), then test:

```bash
curl -I https://myservice.aldof.duckdns.org
```

You should see a `200 OK` (or the appropriate response from your service).

## Pitfalls & Troubleshooting

- **Service not reachable**: Ensure the service is running and reachable via Docker's internal DNS
  from the Traefik container. Test with `docker exec traefik wget -qO- http://<service-name>:<port>/`.
- **502 Bad Gateway**: The service is not running or not listening on the expected port inside the container.
- **Certificate issues**: Check Traefik logs for ACME errors: `docker logs traefik --tail 20`.
- **Router not loading**: Verify the `routes.yml` syntax is correct YAML and that the service name matches.
- **YAML structure error: `rule` in middleware vs router**: The `rule` key belongs ONLY in router definitions.
  Placing it inside a middleware (like `https-redirect`) causes `field not found, node: rule` errors
  and silent route failures. Middlewares only define `redirectScheme` etc.
- **YAML quoting requirement for `rule` values**: The `rule` value in router definitions must be a quoted string
  containing the backtick-delimited host (e.g., `rule: "Host(\`service.example.com\`")`). Missing quotes
  cause YAML parsing errors like `field not found, node: rule` and prevent route loading entirely.
- **Docker DNS resolution failure**: Even with containers on the same network, Traefik's file provider
  sometimes cannot resolve container hostnames via Docker's internal DNS. Fallback: use the host IP
  in the service URL (e.g., `http://192.168.0.5:3001`) instead of the container name.
- **Traefik file provider reload is unreliable**: Configuration changes may not propagate on `docker compose restart`.
  Use full recreate: `docker compose down && docker compose up -d` to force fresh socket bindings and reload.
- **Target service binding to localhost only**: Many services default to `127.0.0.1`. Ensure the service container
  is configured to bind to `0.0.0.0` (e.g., via `HOST_BIND=0.0.0.0` env var) so it's reachable from other containers.
  For FreeLLMAPI specifically, set `HOST_BIND=0.0.0.0` in the `.env` file or Docker compose environment.
- **Service port mismatch**: Double-check that the port in the service definition matches the container's
  exposed port. For FreeLLMAPI, ensure both the container port (3001) and the published port (3001) match.

## Specific fix for Traefik 502 errors
When encountering 502 Bad Gateway errors, verify:
1. The service container is running with `docker ps | grep <service-name>`
2. The service is bound to 0.0.0.0 (not 127.0.0.1) - check container logs or Dockerfile
3. The service URL in routes.yml uses the correct Docker service name and port
4. The routes.yml file has proper YAML syntax with quoted strings for all `rule` values
5. Traefik has been restarted after configuration changes: `docker compose restart traefik` or `docker compose down && docker compose up -d`

## Common configuration errors
- **Incorrect host format**: Using `freellm.aldof.duckdns.org` instead of `Host(\`freellm.aldof.duckdns.org\`)` in the rule
- **Missing quotes**: `rule: Host(\`freellm.aldof.duckdns.org\`)` without surrounding quotes
- **Incorrect service URL**: Using `http://192.168.0.5:8787` instead of `http://myservice:8080` where `myservice` is the Docker service name
- **Service binding issue**: Service container bound to 127.0.0.1 instead of 0.0.0.0, making it unreachable from Traefik
- **Traefik file provider cache**: Configuration changes may not propagate immediately; use `docker compose down && docker compose up -d` to force fresh socket bindings and reload

## Specific fix for Traefik 502 errors
When encountering 502 Bad Gateway errors, verify:
1. The service container is running with `docker ps | grep <service-name>`
2. The service is bound to 0.0.0.0 (not 127.0.0.1) - check container logs or Dockerfile
3. The service URL in routes.yml uses the correct Docker service name and port
4. The routes.yml file has proper YAML syntax with quoted strings for all `rule` values
5. Traefik has been restarted after configuration changes: `docker compose restart traefik` or `docker compose down && docker compose up -d`

## Common configuration errors
- **Incorrect host format**: Using `freellm.aldof.duckdns.org` instead of `Host(\`freellm.aldof.duckdns.org\`)` in the rule
- **Missing quotes**: `rule: Host(\`freellm.aldof.duckdns.org\`)` without surrounding quotes
- **Incorrect service URL**: Using `http://192.168.0.5:8787` instead of `http://myservice:8080` where `myservice` is the Docker service name
- **Service binding issue**: Service container bound to 127.0.0.1 instead of 0.0.0.0, making it unreachable from Traefik
- **Traefik file provider cache**: Configuration changes may not propagate immediately; use `docker compose down && docker compose up -d` to force fresh socket bindings and reload

## Specific fix for Traefik 502 errors
When encountering 502 Bad Gateway errors, verify:
1. The service container is running with `docker ps | grep <service-name>`
2. The service is bound to 0.0.0.0 (not 127.0.0.1) - check container logs or Dockerfile
3. The service URL in routes.yml uses the correct Docker service name and port
4. The routes.yml file has proper YAML syntax with quoted strings for all `rule` values
5. Traefik has been restarted after configuration changes: `docker compose restart traefik` or `docker compose down && docker compose up -d`

## Related

- `freellmapi-integration` skill for a specific example of exposing the FreeLLM API.
- `04-network-traefik/AGENTS.md` in the `01-core-infra` template for domain-specific details.
- `references/fix-traefik-quoting-and-network.md` - Specific fix for Traefik 502 errors due to YAML quoting and service binding issues.
- `references/fix-ansible-hermes-skills-gitconfig.md` - Fix for Ansible hermes-skills role git_config parameter error.
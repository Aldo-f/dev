# Traefik Route Management in 01-core-infra

The Aldo-f infrastructure uses a template-driven approach for Traefik routing. 

## Management Pattern

1. **Templates**: Source files in `~/dev/01-core-infra/templates/infra/04-network-traefik/` (`routes.yml`, `traefik.yml`, `docker-compose.yml`).
2. **Orchestration**: The `containers` role in Ansible (`ansible/roles/containers/`) syncs these templates to `~/dev/04-network-traefik/`.
3. **Registration**: Services are added to `container_services` in `ansible/roles/containers/defaults/main.yml`.

## Pitfall: lineinfile Clobbering

Avoid using Ansible's `lineinfile` with regex on `routes.yml`. 
Example of a dangerous task:
```yaml
- name: Update homepage route
  lineinfile:
    path: "{{ traefik_runtime_dir }}/routes.yml"
    regexp: '^    homepage'
    line: '    homepage-v2:'
```
This regex matches both `homepage-http:` and `homepage:`, causing duplicate lines or truncation. 

**Best Practice**: Always manage the full file via the Ansible `copy` or `template` module from the canonical source in `templates/infra/`.

## Removing Services

When a service is retired (e.g., `plex`):
1. Delete the service runtime directory.
2. Remove the service entry from `ansible/roles/containers/defaults/main.yml`.
3. Remove the router and service definitions from the Traefik templates in `01-core-infra`.
4. Apply changes via `./install.sh`.

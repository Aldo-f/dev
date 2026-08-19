# Infrastructure Verification Pattern

**Trigger**: After deploying infrastructure changes, verify that containers, networks, routes, and health checks are all functioning correctly against the REAL runtime.

**Session Context**: August 2026 - Established three-layer verification after media services deployment

## Three-Layer Verification Stack

### Layer 1: Python Runtime Verification (`tests/verify_deployment.py`)

**Purpose**: Quick shell-out verification against live Docker containers

```bash
python3 tests/verify_deployment.py
```

**Checks**:
- Container running state (docker inspect .State.Running)
- Network attachment (traefik_net presence in NetworkSettings.Networks)
- Traefik routes.yml contains expected hostnames
- Container health status (.State.Health.Status == "healthy")

**Key Implementation**:
```python
def container_network(name, network):
    out, err, rc = run_cmd(f"docker inspect --format='{{{{json .NetworkSettings.Networks}}}}' {name}")
    if rc != 0: return False
    nets = json.loads(out)
    return network in nets

def nextcloud_healthy():
    for name in ["nextcloud-app-1", "nextcloud"]:
        out, err, rc = run_cmd(f"docker inspect --format='{{{{.State.Health.Status}}}}' {name}")
        if rc == 0 and out == "healthy":
            return True
    return False
```

### Layer 2: Ansible Infrastructure Verification (`tests/verify.yml`)

**Purpose**: Declarative assertions using Ansible's module system

```bash
ansible-playbook -i "localhost," tests/verify.yml
```

**Key Patterns**:
```yaml
- hosts: localhost
  connection: local
  vars:
    docker_inspect_format: "{{ '{{' }}json .NetworkSettings.Networks{{ '}}' }}"
    docker_inspect_health: "{{ '{{' }}json .State.Health{{ '}}' }}"
  tasks:
    - shell: "docker inspect plex --format='{{ docker_inspect_format }}'"
      register: plex_net
    - assert: { that: ["'traefik_net' in plex_net.stdout"] }
```

**Template escaping**: Use `{{ '{{' }}` and `{{ '}}' }}` in vars to avoid Jinja2 parsing the docker format string.

### Layer 3: Template Structure Validation

**Purpose**: Validate docker-compose.yml templates before deploy

```bash
python3 -c "
import yaml, os
for f in ['plex','qbittorrent','nextcloud']:
    path = f'templates/infra/05-media-{f}/docker-compose.yml'
    with open(path) as fp: data = yaml.safe_load(fp)
    services = data.get('services', {})
    for name, cfg in services.items():
        assert 'networks' in cfg, f'{name} missing networks'
        assert 'traefik_net' in cfg['networks'], f'{name} not on traefik_net'
        # optional: assert 'healthcheck' in cfg
"
```

## Verification Checklist After Deploy

- [ ] `python3 tests/verify_deployment.py` → All checks passed
- [ ] `ansible-playbook -i "localhost," tests/verify.yml` → All assertions passed
- [ ] Template validation → All templates have networks, restart, healthcheck
- [ ] `docker ps | grep -E 'plex|qbittorrent|nextcloud'` → All running
- [ ] `docker exec traefik cat /etc/traefik/routes.yml | grep -E 'plex|qbittorrent'` → Routes present

### Nextcloud-Specific Verification

- [ ] `.ncdata` file exists in data directory: `ls -la /mnt/HDD1/nextcloud/data/.ncdata`
- [ ] Both Nextcloud app and DB on same network: `docker inspect nextcloud-app-1 | grep traefik_net && docker inspect nextcloud-db-1 | grep traefik_net`
- [ ] MariaDB users created: `docker exec nextcloud-db-1 mysql -u root -pchangeme_root -e "SELECT User FROM mysql.user;" | grep nextcloud`
- [ ] Nextcloud install complete: `docker exec nextcloud-app-1 php occ status | grep "installed: true"`
- [ ] HTTPS redirect works: `curl -sk -I https://cloud.aldof.duckdns.org | grep "HTTP/2 302"`
- [ ] Login page loads: `curl -sk -L https://cloud.aldof.duckdns.org/login | grep -c "Nextcloud"`

### Nextcloud Container Naming Note (2026-08-13)
The actual Nextcloud container name when deployed via the containers role is `05-media-nextcloud-app-1` (Docker Compose project prefix). Verification scripts should check for this name specifically, not `nextcloud` or `nextcloud-app-1`.

### Full Subdomain Verification (2026-08-08)

```bash
# Test all dev-subdomains are accessible via Traefik with IP allowlist
curl -sk -I https://freellm.aldof.duckdns.org          # 200
curl -sk -I https://web.hermes.dev.aldof.duckdns.org   # 501 (SPA serves HTML)
curl -sk -I https://cloud.aldof.duckdns.org            # 302 (login redirect)
curl -sk -I https://aldof.duckdns.org                  # 200 (homepage)
curl -sk -I https://vault.aldof.duckdns.org            # 200
curl -sk -I https://portainer.aldof.duckdns.org        # 307 (redirect)
curl -sk -I https://cockpit.aldof.duckdns.org          # 301 (redirect)
curl -sk -I https://plex.aldof.duckdns.org             # 401 (auth required)
curl -sk -I https://qbittorrent.aldof.duckdns.org      # 200
curl -sk -I https://torrent.aldof.duckdns.org          # 200 (alias)

# Verify IP allowlist is active
docker exec traefik cat /etc/traefik/routes.yml | grep -A 8 "ipAllowList:"

# Verify all services use the middleware
docker exec traefik cat /etc/traefik/routes.yml | grep -c "ipAllowList"  # Should be 18 (2 per router x 9 routers)
```

## Common Pitfalls Avoided

| Pitfall | Detection | Fix |
|---------|-----------|-----|
| Container running but not on traefik_net | Layer 1 & 2 network check | Fix compose template networks section |
| Health check returns null | Layer 1 health check | Add healthcheck: section to compose |
| Routes missing from routes.yml | Layer 1 & 2 routes check | Update templates/infra/04-network-traefik/routes.yml |
| nextcloud-app-1 vs nextcloud container name | Layer 1 tries both names | Accept either container name for health |
| Missing `.ncdata` file | `ls /mnt/HDD1/nextcloud/data/.ncdata` should exist | Create with `echo "# Nextcloud data directory" > .ncdata` |
| DB not on same network as app | Both must be on `traefik_net` in compose template | Update compose to put db and app on same network |
| MariaDB users not created | Volume has stale data - run `docker compose down -v` and recreate | Remove volume before deploy to trigger fresh init |

## Key Principle

**ALWAYS test against REAL runtime containers, not just template files or venv-interpreted paths.** The user pushes back on unverified results - show actual docker inspect output and test results before claiming success.

---

## Project Structure Reorganization (2026-08-04)

### Scripts Directory Pattern

```
/scripts/
├── deploy.sh              # Main deployment entry point
├── operations/            # Recurring operational scripts
│   ├── backup.sh
│   └── healthcheck.sh
├── traefik/               # Traefik-specific management
│   └── reload_traefik.sh
├── hermes/                # Hermes/mem0 management
│   └── setup-mem0.sh
└── podman/                # Podman deployment helpers
    └── deploy.sh
```

### Cron Template Updates

```yaml
# templates/cron/01-core-infra.cron
*/15 * * * * __USER__ __CORE_INFRA__/scripts/operations/healthcheck.sh >> __CORE_INFRA__/logs/health-cron.log 2>&1
0 3 * * * __USER__ __CORE_INFRA__/scripts/operations/backup.sh >> __CORE_INFRA__/logs/backup-cron.log 2>&1
```

### Ansible Role Path Updates

```yaml
# ansible/roles/cron/tasks/main.yml
- name: Copy backup.sh to bin
  copy:
    src: "{{ infra_dir }}/scripts/operations/backup.sh"
    dest: "/usr/local/bin/backup.sh"
    mode: '0755'
    force: no  # Only copy if content differs
```

### Template Validation Pattern

Quick YAML syntax + structure validation:
```bash
python3 -c "
import yaml, os, sys
templates = [
    'templates/infra/05-media-plex/docker-compose.yml',
    'templates/infra/05-media-qbittorrent/docker-compose.yml',
    'templates/infra/05-media-nextcloud/docker-compose.yml',
]
for t in templates:
    if not os.path.exists(t):
        print(f'MISSING: {t}')
        sys.exit(1)
    data = yaml.safe_load(open(t))
    services = data.get('services', {})
    for name, cfg in services.items():
        assert 'networks' in cfg, f'{t}: {name} missing networks'
        if name != 'db':  # db doesn't need external network
            assert 'traefik_net' in cfg['networks'], f'{t}: {name} missing traefik_net'
print('All templates valid')
"
```

### Verification Checklist After Deployment

Run both verification layers:
```bash
# Layer 1: Fast ad-hoc check
python3 tests/verify_deployment.py

# Layer 2: Ansible-native validation
ansible-playbook -i "localhost," tests/verify.yml
```

Expected output: All checks pass (9/9 Python, 10/10 Ansible).

### Integration with CI/CD

Add to GitHub Actions workflow:
```yaml
- name: Verify deployment
  run: |
    python3 tests/verify_deployment.py
    ansible-playbook -i "localhost," tests/verify.yml
  env:
    DOCKER_HOST: unix:///var/run/docker.sock
```

### Common Pitfalls

| Issue | Solution |
|-------|----------|
| Nextcloud healthcheck fails | Check container name is `nextcloud-app-1`, not `nextcloud` |
| Ansible template escaping | Use `{{ '{{' }}` and `{{ '}}' }}` for literal braces |
| `command` module fails with templates | Use `shell` module instead |
| Traefik route verification | Use `slurp` + `b64decode` for file content |
| Cron script path changes | Update both cron template AND Ansible role task |
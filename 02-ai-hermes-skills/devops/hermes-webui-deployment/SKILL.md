---
name: hermes-webui-deployment
category: devops
description: Deploy Hermes WebUI via Ansible idempotently
---

# Hermes WebUI Deployment via Ansible (01-core-infra)

**Trigger**: When you need to ensure Hermes WebUI is properly deployed and configured as part of the 01-core-infra infrastructure setup.

## Two Deployment Modes

### Mode A: Docker Container (RECOMMENDED — integrates with Traefik)
Deploys Hermes WebUI as a Docker container on the `traefik_net` network. This is the **current recommended approach** because it integrates with Traefik for HTTPS access at `https://web.hermes.dev.aldof.duckdns.org/` and provides bare server access via volume mounts.

**Key Patterns**:
- Template: `templates/infra/02-ai-hermes-webui/docker-compose.yml`
- Build context: `/home/aldo/dev/02-ai-hermes-webui` (source repo)
- Runtime dir: `/home/aldo/dev/02-ai-hermes-webui` (same as build context)
- Volumes: `__HOME__/.hermes` and `__HOME__/workspace` for bare server access
- Traefik route: `web.hermes.dev.aldof.duckdns.org` → `http://hermes-webui:8787`
- IP allowlist middleware applied (dev subdomain)

**Required Changes** (see `references/hermes-webui-docker-deployment-plan.md` for full details):
1. Add to `container_services` in `ansible/roles/containers/defaults/main.yml`
2. Fix docker-compose.yml template with `__HOME__` and `__CORE_INFRA__` placeholders
3. Disable systemd service to avoid port conflict

### Mode B: Systemd Service (LEGACY — direct host deployment)
Runs Hermes WebUI directly on the host via systemd. Use only if Docker deployment is not possible.

**Key Patterns**:
- Deploy to `/home/aldo/dev/02-ai-hermes-webui`
- Use `become: no` for git operations and file checks
- Use `become: true` only for systemd service file deployment
- Use `lookup('env', 'HOME')` to get the real user's home directory
- Ensure service file includes `Environment=HERMES_WEBUI_HOST=0.0.0.0` for LAN access
- Service uses `start.sh` script from the repo

**Idempotent Tasks to Add to site.yml** (LEGACY):

```yaml
# HERMES WEBUI DEPLOYMENT TASKS (Systemd mode - legacy)
- name: Ensure hermes-webui directory exists
  file:
    path: "{{ lookup('env', 'HOME') }}/dev/02-ai-hermes-webui"
    state: directory
    owner: aldo
    group: aldo
  become: false

- name: Clone or update hermes-webui repo
  git:
    repo: https://github.com/nesquena/hermes-webui.git
    dest: "{{ lookup('env', 'HOME') }}/dev/02-ai-hermes-webui"
    version: main
    force: yes
  become: false

- name: Ensure start.sh is executable
  file:
    path: "{{ lookup('env', 'HOME') }}/dev/02-ai-hermes-webui/start.sh"
    mode: '0755'
  become: false

- name: Deploy hermes-webui systemd service
  copy:
    dest: /etc/systemd/system/app-hermes-webui.service
    content: |
      [Unit]
      Description=Hermes WebUI Service
      After=network.target

      [Service]
      Environment=HERMES_WEBUI_HOST=0.0.0.0
      ExecStart={{ lookup('env', 'HOME') }}/dev/02-ai-hermes-webui/start.sh
      WorkingDirectory={{ lookup('env', 'HOME') }}/dev/02-ai-hermes-webui
      Restart=always
      User={{ ansible_user_id }}

      [Install]
      WantedBy=multi-user.target
    owner: root
    group: root
    mode: '0644'
  notify:
    - Reload systemd
    - Enable and start hermes-webui
```

**Handlers to Add**:
```yaml
  handlers:
    - name: Reload systemd
      command: systemctl daemon-reload

    - name: Enable and start hermes-webui
      systemd:
        name: app-hermes-webui.service
        enabled: yes
        state: started
```

**Common Pitfalls**:
- Using `ansible_env.HOME` with `become: true` resolves to `/root` instead of `/home/aldo` - use `lookup('env', 'HOME')` instead
- Forgetting to set `become: false` for git/file operations (they work fine as the regular user)
- Not setting proper ownership on the deployed directory (should be aldo:aldo)
- Using hardcoded paths instead of leveraging the HOME environment variable
- Forgetting to notify handlers to actually start/enable the service after deploying the unit file

**Verification Steps**:
1. After running the playbook, check: `systemctl status app-hermes-webui.service`
2. Verify it's active and listening on port 8787: `ss -tlnp | grep 8787`
3. Confirm it's accessible from another machine on your LAN: `http://<your-pi-ip>:8787`
4. Check the service file: `cat /etc/systemd/system/app-hermes-webui.service`
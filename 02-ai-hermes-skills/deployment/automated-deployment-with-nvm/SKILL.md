---
name: automated-deployment-with-nvm
description: Bare-metal NVM + git-clone app deployments on Pi via Ansible.
---

# Automated Pi deployment with NVM & git-clone apps

**Trigger**: Setting up a fresh Pi (or re-provisioning) where you need:
- Node.js via NVM (bare-metal, not containerized)
- One or more apps deployed from git repos into `~/dev/06-apps-*`

## 1. NVM bare-metal install (runs once per Pi)

```yaml
# roles/tools/defaults/main.yml  – add to tools_sentries
nvm:
  command: nvm --version
```

```yaml
# roles/tools/tasks/main.yml  – tasks inserted before other tools
- name: Download and install NVM
  shell: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.6/install.sh | bash
  args:
    creates: "{{ ansible_env.HOME }}/.nvm/nvm.sh"
  when: "'nvm' in tools_sentries"

- name: Load NVM and verify
  shell: |
    export NVM_DIR="{{ ansible_env.HOME }}/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    command -v nvm
  when: "'nvm' in tools_sentries"

- name: Install LTS Node.js via NVM
  shell: |
    export NVM_DIR="{{ ansible_env.HOME }}/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install --lts
    nvm use --lts
  args:
    creates: "{{ ansible_env.HOME }}/.nvm/versions/node/v*/bin/node"
  when: "'nvm' in tools_sentries"
```

## 2. Generic git-clone → deploy pattern (repeatable per app)

Each app lives in its own git repo.  The playbook:

1. Clones/updates the repo to `~/dev/06-apps-<name>/`
2. Runs `ansible-playbook` **inside that repo** (so the app owns its own deploy logic)
3. Optionally symlinks the repo's `infra/` into `~/dev/01-core-infra/templates/infra/06-apps-<name>/` for system-level compose files.

Example for **toerekening**:

```yaml
# playbooks/site.yml  – one block per app
- name: Ensure toerekening repo exists
  git:
    repo: "https://github.com/your-org/06-apps-toerekening.git"
    dest: "{{ dev_home }}/06-apps-toerekening"
    version: main
    update: yes

- name: Run toerekening's own deploy playbook
  command: ansible-playbook -i inventories/local.yml playbooks/deploy.yml
  args:
    chdir: "{{ dev_home }}/06-apps-toerekening"
  when: "'toerekening' in apps_to_deploy"
```

**App-side `deploy.yml`** (inside the cloned repo) handles:
- Copying its own `Dockerfile`, `docker-compose.yml`, `.env.template` → `.env`
- `docker compose up -d`
- Any migrations, seed scripts, etc.

## 3. Adding a new app

1. Create repo `06-apps-<name>` with its own `playbooks/deploy.yml`
2. Add one block in `site.yml` (see toerekening example)
3. Add `<name>` to `apps_to_deploy` list in `group_vars/all.yml`

## Variables

```yaml
# group_vars/all.yml
dev_home: "/home/aldo/dev"
apps_to_deploy:
  - toerekening
  # - next-app
  # - another-app
```

## Pitfalls & fixes

| Issue | Fix |
|-------|-----|
| `docker compose` fails if docker not started | `systemctl enable --now docker` in `roles/base/tasks/main.yml` |
| NVM not in PATH for Ansible tasks | Always `export NVM_DIR=... && source $NVM_DIR/nvm.sh` inside each `shell:` |
| `.env` missing | Ship `.env.template` in repo; deploy task copies to `.env` if absent |
| Port conflicts | Each app gets its own compose network; Traefik labels handle routing |

## Verification

```bash
# After full run
nvm --version        # 0.40.6
node -v              # v24.x LTS
ls ~/dev/06-apps-*/  # each app dir exists with docker-compose.yml
docker ps            # each app's containers running
```
---
name: ansible-troubleshooting
category: devops
description: Fix Raspberry Pi Ansible failures.
---

# Ansible Troubleshooting — Raspberry Pi

**Trigger**: When Ansible playbooks fail on Raspberry Pi / Debian targets with npm, docker, permission issues, or when deploying self-hosted AI services (memory backends, LLM proxies) via Ansible.

## Pi-Specific Deployment Patterns

### Traefik Deployment on Pi

1. **Define absolute paths** – set `script_dir` to the repository root. This ensures `template_dir` resolves correctly and avoids the `/workdir` fallback.
2. **Create the Docker network** – use the `command` module rather than `community.docker.docker_network` (which may be missing):
   ```yaml
   - name: Ensure Traefik network exists
     ansible.builtin.command: docker network create {{ traefik_network }}
     ignore_errors: true
     failed_when: false
   ```
3. **Copy template files** – use `ansible.builtin.copy` with a loop; set `owner`/`group` to the non-root user.
4. **Create Docker volumes** – via `command` for idempotency.

### Node.js / npm Tasks via Ansible

**Critical order: Fix ownership first, then run npm as the real user.**
1. Fix ownership FIRST (as root, `become: true` + `file` module)
2. THEN run npm commands (as the real user, `become: false`)
3. Reversing these steps results in root-owned `node_modules` that fail on subsequent runs.

```yaml
- name: Ensure correct ownership of repo directory
  file:
    path: /home/aldo/dev/<repo>
    owner: aldo
    group: aldo
    recurse: yes
  become: true

- name: Install Node.js dependencies
  become: false
  shell: |
    export NVM_DIR="/home/aldo/.nvm"
    source "$NVM_DIR/nvm.sh"
    cd /home/aldo/dev/<repo>
    npm config set unsafe-perm true
    npm ci --legacy-peer-deps
  environment:
    PATH: "/home/aldo/.nvm/versions/node/v24.18.0/bin:/home/aldo/.nvm:/bin:$PATH"
    NVM_DIR: "/home/aldo/.nvm"
```

**Pitfalls:**
- Running `npm ci` as root leaves root-owned files; subsequent runs hit `EACCES`.
- `npm config set unsafe-perm true` not `--unsafe-perm` (deprecated in npm 10+).
- `--legacy-peer-deps` is often needed with React 19 / Docusaurus.
- Always add `/bin` to `PATH` — Ansible's sanitized PATH may omit it, causing `ENOENT` in lifecycle scripts.
- The `npm` Ansible module cannot find nvm-managed node; use `shell` with explicit NVM_DIR.

### Modern Ansible Playbook Structure (user correction)

Based on user feedback, corrected the typical Ansible playbook structure for package installation:

```yaml
- name: Install Docker, Docker Compose, Node.js, npm, and tree via apt
  apt:
    name:
      - docker.io
      - docker-compose
      - nodejs
      - npm
      - tree
    state: present
    update_cache: yes

- name: Install omo via npm
  command: npm install -g omo
  become: true

- name: Install opencode via npm
  command: npm install -g opencode-ai
  become: true

- name: Install lazycodex-ai via npm
  command: npm install -g lazycodex-ai
  become: true

- name: Install bun via official installer
  shell: curl -fsSL https://bun.com/install | bash
  args:
    executable: /bin/bash
  become_user: aldo

- name: Install oh-my-openagent via bunx
  command: bunx oh-my-openagent install
  become_user: aldo

- name: Create opencode config directory
  file:
    path: /home/aldo/.config/opencode
    state: directory
    mode: '0755'
```

**User workflow corrections:**
1. Separate apt package installation from tool-specific installations (npm, bun)
2. Use `shell` module for bun installer (curl pipeline) instead of `command` module
3. Use `become_user` parameter for bun installation (targets `aldo` user)
4. Proper tool sentry ordering in `tools_sentries` section

### mem0 Self-Hosted Memory Backend (Pi)

mem0 OSS mode runs entirely in-process (no Docker server needed). Architecture for Pi 5:

| Component | Tool | Config |
|-----------|------|--------|
| Vector DB | Qdrant (local/embedded) | `~/.hermes/mem0_qdrant/` |
| Embeddings | Ollama → `nomic-embed-text` (768d) | `localhost:11434` |
| LLM | FreeLLM or any OpenAI-compatible API | as configured in `mem0.json` |

**Ansible deployment block** (gated via `tools_sentries`):
```yaml
- name: Setup mem0 memory backend
  block:
    - name: Install mem0 pip packages
      pip:
        name: [mem0ai, qdrant-client]
        state: present
        executable: /home/aldo/.hermes/hermes-agent/venv/bin/python3 -m pip

    - name: Ensure Ollama embedding model is available
      command: ollama pull nomic-embed-text
      become: false
      changed_when: "'pulling' in ollama_pull.stdout"
      failed_when: false

    - name: Ensure Qdrant storage directory exists
      file:
        path: /home/aldo/.hermes/mem0_qdrant
        state: directory
        owner: aldo
        group: aldo
        mode: "0755"

    - name: Pre-initialize Qdrant collection
      script: scripts/setup-mem0.sh
      become: false
      changed_when: "'Created' in mem0_setup.stdout or 'Recreated' in mem0_setup.stdout"

    - name: Enable mem0 in Hermes config
      command: hermes config set memory.provider mem0
      become: false
      changed_when: "'Set' in mem0_config.stdout"
  when: "'mem0' in tools_sentries"
```

**Key pitfalls**:
- Qdrant Docker images **will not run on Pi 5** (16KB kernel pages crash jemalloc) — see `references/qdrant-pi-jemalloc.md`
- The `pip` module needs `executable:` pointing to the Hermes venv pip, not system pip
- Hermes memory provider only activates on `/reset` or next session, not mid-conversation
- mem0 OSS config lives in `~/.hermes/mem0.json`, not in Hermes config.yaml

## Common Pitfalls (General)

- `npm: command not found` → npm not installed or not in PATH. Fix: `sudo apt-get install -y npm`.
- Role tasks not executing → the role is not included in `site.yml`. Check if tasks are inlined vs. loaded from a role.
- Docker socket permission denied → user not in docker group. Fix: `sudo usermod -aG docker aldo && sudo systemctl restart docker`.
- `BASH_SOURCE[0]: unbound variable` when script is piped → avoid relying on BASH_SOURCE; use hardcoded paths.
- `ansible_env.HOME` resolves to `/root` when using `become: true` → use `lookup('env', 'HOME')` to get the actual user's home directory.

### PEP 668 — Externally Managed Python (Debian/Raspberry Pi)

Debian-based systems (including Raspberry Pi OS) block system-wide `pip install` with:
```
error: externally-managed-environment
× This environment is externally managed
```

**Workaround:** Always use a virtualenv when installing Python packages via Ansible on Pi.

```yaml
# Option 1: Create a venv first, then pip-install inside it
- name: Create spec‑kit virtualenv
  command: python3 -m venv /home/{{ ansible_user }}/.local/spec-kit-venv
  args:
    creates: /home/{{ ansible_user }}/.local/spec-kit-venv/bin/python

- name: Install spec‑kit Python package in venv
  pip:
    name: /home/{{ ansible_user }}/.local/spec-kit
    editable: true
    state: present
    executable: /home/{{ ansible_user }}/.local/spec-kit-venv/bin/pip
```

After installing, add the venv's `bin/` directory to the user's `PATH` in `.bashrc` or `.config/fish/config.fish`.

**Setting the tool sentry command**: the sentry in `defaults/main.yml` must point to the venv binary path:

```yaml
spec_kit:
  command: '/home/aldo/.local/spec-kit-venv/bin/specify --version'
```

### Tool Sentry Lifecycle (Adding a New Tool)

Every new tool added to the infrastructure follows a 4-step pattern:

1. **Declare a sentry** in `ansible/roles/tools/defaults/main.yml`:

   ```yaml
   tools_sentries:
     my_tool:
       command: my-tool --version
   ```

2. **Add install task(s)** in `ansible/roles/tools/tasks/main.yml`, gated on the sentry:

   ```yaml
   - name: Install my_tool (clone repository)
     git:
       repo: https://github.com/org/my-tool.git
       dest: "/home/{{ ansible_user }}/.local/my-tool"
       version: main
       update: yes
     when: "'my_tool' in tools_sentries"

   - name: Install my_tool (pip/packaging step)
     pip:
       name: "/home/{{ ansible_user }}/.local/my-tool"
       editable: true
       state: present
       executable: "/home/{{ ansible_user }}/.local/my-tool-venv/bin/pip"
     when: "'my_tool' in tools_sentries"
   ```

3. **Add PATH configuration** so the tool is discoverable in subsequent shells:

   ```yaml
   - name: Add my_tool to bash PATH
     lineinfile:
       path: /home/{{ ansible_user }}/.bashrc
       line: 'export PATH="$HOME/.local/my-tool-venv/bin:$PATH"'
       create: yes
       insertafter: EOF
     when: "'my_tool' in tools_sentries"
   ```

4. **Add post-install verification** in the consuming role:

   ```yaml
   - name: Verify my_tool works after deployment
     command: my-tool --version
     register: tool_check
     changed_when: false
     failed_when: tool_check.rc != 0
   ```

**Pitfalls**
- Don't forget to handle PEP 668 for Python tools — always use a venv.
- The sentry command must exactly match what a future shell invocation will resolve (full path for venv binaries).
- `when: "'my_tool' in tools_sentries"` checks if the sentry key exists, not whether the binary is present — keep the sentry definition and the install task in sync.

## Debugging Checklist

1. Is npm installed? `which npm` or `npm --version`
2. Is PATH correct? `echo $PATH` as the target user
3. Is docker socket accessible? `ls -la /var/run/docker.sock` and `groups aldo`
4. Is the node_modules directory clean? `ls node_modules` after deletion and retry
5. Run playbook with verbose output: `ansible-playbook -vvv site.yml`
6. After modifying the package list, run a local syntax check and dry-run:
   ```bash
   ansible-playbook -i 'localhost,' -c local --syntax-check ansible/playbooks/site.yml
   ansible-playbook -i 'localhost,' -c local ansible/playbooks/site.yml --check --diff
   ```
7. Keep `gather_facts` as a boolean (`true`/`false`).

## CI/CD Pipeline Pitfalls

1. **Complex Docker Builds** — Log failures without failing the entire workflow.
2. **Ansible Module FQCN** — Use fully qualified names (`ansible.builtin.command`, `ansible.builtin.file`, `ansible.builtin.copy`, `ansible.builtin.git`, `ansible.builtin.shell`, `ansible.builtin.apt`) instead of deprecated bare names.
3. **GitHub Actions YAML** — Use `--format standard` for yamllint; fix missing `---`, truthy values, trailing newlines.
4. **Virtual Environment Management** — Use `python3 -m venv .venv` and source before installing packages.
5. **Docker User Permissions** — Ensure docker group membership and socket permissions in CI.
6. **GitHub Actions Token Scope** — Require `contents: read`, `actions: read` permissions.
7. **Environment Variables** — Set `DEBIAN_FRONTEND=noninteractive`, `LANG=C.UTF-8`, proper PATH.

## ShellCheck integration

When adding ShellCheck to the Ansible tools role, include a sentinel and an installation task. The sentinel (`shellcheck: command: shellcheck -V`) enables the role to detect whether ShellCheck is already present. The task installs it via `apt-get` and is idempotent:

```yaml
- name: Install ShellCheck
  shell: sudo apt-get update && sudo apt-get install -y shellcheck
  args:
    creates: /usr/bin/shellcheck
  become: true
  when: "'shellcheck' in tools_sentries"
```

Add this to `ansible/roles/tools/defaults/main.yml` and `ansible/roles/tools/tasks/main.yml`. Keep the task order after the TailScale block.

## References

- `references/qdrant-pi-jemalloc.md` — Qdrant Docker crash on Pi 5 (16KB pages, jemalloc incompatibility) and local-mode workaround.

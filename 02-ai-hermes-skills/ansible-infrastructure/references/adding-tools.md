# Adding New Tools to Ansible Playbook

## Overview
This document documents the process for adding new CLI tools to the 01-core-infra Ansible playbook, following the tool sentry pattern.

## Recent Example: Adding locate (plocate)

### Problem
User wanted faster file searching capability via the `locate` command instead of relying solely on `find`.

### Solution Implemented
1. Added sentry entry in `ansible/roles/tools/defaults/main.yml`:
   ```yaml
   locate:
     command: locate --version
   ```

2. Added installation task in `ansible/roles/tools/tasks/main.yml`:
   ```yaml
   - name: Install locate (plocate)
     apt:
       name: locate
       state: present
     become: true
     when: "'locate' in tools_sentries and ansible_facts.packages['locate'] is not defined"
   ```

3. Activated the tool in `ansible/playbooks/site.yml` by adding `locate` to the `tools_sentries` list.

### Verification
- Playbook syntax check passed: `ansible-playbook --syntax-check playbooks/site.yml`
- Installation verified via `command -v locate updatedb`
- Database built successfully with `sudo updatedb`
- Functionality tested with `locate thuis-v4 | head -10`

## Recent Example: Adding Camoufox (Complex Python Tool with Virtual Environment)

### Problem
User wanted to integrate Camoufox (anti-detect Firefox-based browser for AI agents) into the infrastructure for use with Hermes browser automation. This tool requires Python virtual environment isolation, multiple pip packages, and post-install commands.

### Solution Implemented
1. Added sentry entry in `ansible/roles/tools/defaults/main.yml`:
   ```yaml
   camoufox:
     command: camoufox --version
   ```

2. Created dedicated role `ansible/roles/camoufox/tasks/main.yml` for complex installation:
   ```yaml
   - name: Install camoufox via pip in dedicated virtual environment
     shell: |
       mkdir -p /home/aldo/.venv-camoufox
       python3 -m venv /home/aldo/.venv-camoufox
       . /home/aldo/.venv-camoufox/bin/activate
       pip install --upgrade pip
       pip install "camoufox[geoip]" camoufox-cli==0.4.0
       camoufox --version
       camoufox fetch
       camoufox sync
     environment:
       PATH: "{{ ansible_env.PATH }}:/home/aldo/.venv-camoufox/bin"
     args:
       creates: /home/aldo/.venv-camoufox

   - name: Add camoufox to system PATH permanently
     lineinfile:
       path: /home/aldo/.bashrc
       line: 'export PATH="$HOME/.venv-camoufox/bin:$PATH"'
       create: yes
       insertafter: EOF
     when: "'camoufox' in tools_sentries"
   ```

3. Added template documentation in `templates/infra/camoufox/CAMOUFOX.md`

4. Updated Hermes config (`~/.hermes/config.yaml`) to use Camoufox as browser backend:
   ```yaml
   browser:
     backend: camoufox
     inactivity_timeout: 120
     cloud_provider: local
     use_gateway: false
   ```

### Verification
- Playbook syntax check passed
- Virtual environment created at `~/.venv-camoufox/`
- PATH export added to `~/.bashrc`
- `camoufox --version` works after sourcing bashrc
- Browser navigation test passed (Google Form loaded successfully)

## General Pattern for Complex Tools
For tools requiring virtual environments, multiple dependencies, or post-install setup:

1. **Sentry declaration** (`defaults/main.yml`) - simple version check
2. **Dedicated role** (`ansible/roles/<tool-name>/tasks/main.yml`) - full installation logic with venv isolation
3. **PATH management** - permanent export to shell config
4. **Template documentation** (`templates/infra/<tool-name>/`) - usage and configuration
5. **Application integration** - configure dependent services (e.g., Hermes browser backend)

## Best Practices
- Always use the tool sentry pattern - never hard-code installations elsewhere
- Use appropriate `when` conditions to avoid re-installing existing tools
- For apt packages, include `ansible_facts.packages['<package>'] is not defined` check
- For Python tools, use dedicated virtual environments (`python3 -m venv`)
- Use `creates` argument for idempotency
- Keep sentry commands simple and reliable (usually `--version` or `-v`)
- Test the sentry command manually before adding to ensure it works as expected
- Add PATH exports to appropriate shell config (`.bashrc`, `.zshrc`, or fish config)
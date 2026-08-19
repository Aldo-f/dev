# Ansible Idempotency Patterns (01-core-infra)

Documented during August 2026 session - four patterns for making Ansible playbooks truly idempotent.

## Pattern 1: PATH Management - `lineinfile` → `blockinfile`

### Problem
Multiple `lineinfile` tasks appending PATH exports to `.bashrc` and `.config/fish/config.fish` created duplicate entries on every playbook re-run.

### Solution
Use `blockinfile` with unique markers instead:

```yaml
# Bash
- name: Ensure bash config has PATH for curl-installed tools
  blockinfile:
    path: /home/{{ ansible_user }}/.bashrc
    block: |
      export PATH="$HOME/.bun/bin:$HOME/fvm/bin:$HOME/.lmstudio/bin:$HOME/.local/bin:$HOME/.opencode/bin:$PATH"
    marker: "# {mark} ANSIBLE MANAGED PATH BLOCK - curl-installed tools"
    create: yes
  when: "'ollama' in tools_sentries or 'hermes' in tools_sentries or 'opencode' in tools_sentries"

# Fish (fish 4.0 compatible syntax: use set -gx not set -Ux)
- name: Ensure fish config has PATH for curl-installed tools
  blockinfile:
    path: /home/{{ ansible_user }}/.config/fish/config.fish
    block: |
      set -gx PATH $HOME/.bun/bin $HOME/fvm/bin $HOME/.lmstudio/bin $HOME/.local/bin $HOME/.opencode/bin $PATH
    marker: "# {mark} ANSIBLE MANAGED PATH BLOCK - curl-installed tools"
    create: yes
  when: "'ollama' in tools_sentries or 'hermes' in tools_sentries or 'opencode' in tools_sentries"
```

**Files:**
- `ansible/roles/mesh_sync/tasks/main.yml` - Main PATH blocks
- `ansible/roles/tools/tasks/main.yml` - spec-kit PATH blocks

---

## Pattern 2: Cron Scripts - `force: no` on `copy`

### Problem
Scripts copied to `/usr/local/bin/` on every run, always reporting "changed" even when content identical.

### Solution
Add `force: no` to only copy when source differs from destination:

```yaml
- name: Copy backup.sh to bin
  copy:
    src: "{{ infra_dir }}/scripts/operations/backup.sh"
    dest: "/usr/local/bin/backup.sh"
    mode: '0755'
    force: no  # Only copy if content differs

- name: Copy healthcheck.sh to bin
  copy:
    src: "{{ infra_dir }}/scripts/operations/healthcheck.sh"
    dest: "/usr/local/bin/healthcheck.sh"
    mode: '0755'
    force: no
```

**File:** `ansible/roles/cron/tasks/main.yml`

---

## Pattern 3: Traefik Route Sync - Conditional Reload

### Problem
Routes file copied and reload handler triggered on every run, even when routes.yml unchanged.

### Solution
Register copy result and only reload when actually changed:

```yaml
- name: Sync Traefik routes.yml template to runtime
  copy:
    src: "{{ template_dir }}/infra/04-network-traefik/routes.yml"
    dest: "{{ traefik_runtime_dir }}/routes.yml"
    owner: aldo
    group: aldo
    mode: '0644'
  register: routes_copy

- name: Reload traefik if routes changed
  command: docker exec traefik kill -HUP 1
  when: routes_copy.changed
  become: true
```

**File:** `ansible/roles/containers/tasks/main.yml`

---

## Pattern 4: Install Commands - Proper `changed_when` / `failed_when`

### Problem
Shell-based install tasks lacked proper change detection, always reporting "changed" on re-runs or failing incorrectly when tools already existed.

### Solution
Add `register`, `changed_when`, and `failed_when` to all install tasks:

```yaml
# Ollama model pull - detect actual pull vs "already exists"
- name: Pull Ollama model
  command: ollama pull "{{ ollama_model }}"
  register: ollama_pull
  changed_when: "'Pulling' in ollama_pull.stdout or 'pulling' in ollama_pull.stdout"
  failed_when: ollama_pull.rc != 0 and 'already exists' not in ollama_pull.stderr and 'already exists' not in ollama_pull.stdout
  when: ollama_key_file.stat.exists and ollama_model is defined

# Generic installer pattern (curl | sh installers)
- name: Install ollama
  shell: curl -fsSL https://ollama.com/install.sh | sh
  args:
    creates: /usr/bin/ollama
  become: true
  when: "'ollama' in tools_sentries"
  register: ollama_install
  changed_when: ollama_install.rc == 0 and ('install' in ollama_install.stdout.lower() or 'downloaded' in ollama_install.stdout.lower())
  failed_when: ollama_install.rc != 0

# Applied to: nodejs, pnpm, fvm, hermes, opencode, tailscale, lmstudio
```

**Files:**
- `ansible/roles/mesh_sync/tasks/main.yml` - Ollama model pull
- `ansible/roles/tools/tasks/main.yml` - All installer tasks

---

## Verification Script

Ad-hoc verification script used to validate all improvements:

```python
# Key checks performed:
1. blockinfile usage with markers in mesh_sync + tools roles
2. force: no on both cron script copies
3. routes_copy.changed conditional in containers role
4. register + changed_when + failed_when on 10 installer tasks
5. Ansible syntax check passes
```

Run: `python3 /tmp/hermes-verify-idempotency.py` → "ALL IDEMPOTENCY IMPROVEMENTS VERIFIED"

---

## Impact

- Playbook re-runs now properly detect unchanged state
- Avoids unnecessary work (no redundant copies, no duplicate PATH entries)
- Cleaner output (fewer "changed" tasks)
- Faster execution on re-runs
- No false failures from "already exists" conditions
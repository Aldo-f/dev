# NVM as Root Pitfall

## Problem
When `become: true` is set at the Ansible play level, all tasks run as root by default. NVM's `$HOME` resolves to `/root`, so NVM_DIR paths break silently:
- `nvm: command not found` (exit 127)
- Node/npm not found even though they were "installed"

## Root Cause
The NVM install script sets up `~/.nvm` under the current user's home. When run as root, it installs to `/root/.nvm`. Subsequent tasks that source `~/.nvm/nvm.sh` as the target user (`aldo`) find nothing because `/home/aldo/.nvm` doesn't exist.

## Fix
Every NVM-related task must specify both:
1. `become_user: aldo` — so NVM installs under the right home
2. Absolute `NVM_DIR="/home/aldo/.nvm"` — not `$HOME/.nvm`

```yaml
- name: Download and install NVM
  shell: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.6/install.sh | bash
  args:
    creates: /home/aldo/.nvm/nvm.sh
  become_user: aldo
  when: "'nvm' in tools_sentries"

- name: Install and activate LTS Node.js version via NVM
  shell: |
    export NVM_DIR="/home/aldo/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install --lts
    nvm use --lts
  args:
    creates: /home/aldo/.nvm/versions/node/v*/bin/node
  become_user: aldo
  when: "'nvm' in tools_sentries"
```

## Verification
After installation:
```bash
# As aldo user
/home/aldo/.nvm/versions/node/v24.18.0/bin/node -v
/home/aldo/.nvm/versions/node/v24.18.0/bin/npm -v
```

## Related
- See `../SKILL.md` for the full playbook structure with NVM tasks
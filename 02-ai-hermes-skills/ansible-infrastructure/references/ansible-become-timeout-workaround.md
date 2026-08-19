# Ansible Become Timeout Workaround

## Problem
When running `ansible-playbook` on `localhost` with `connection: local`, tasks with `become: true` can time out with the error:
```
[ERROR]: Task failed: Timed out waiting for become success.
fatal: [localhost]: UNREACHABLE! => {"msg": "Task failed: Timed out waiting for become success.", "unreachable": true}
```
This occurs even when passwordless sudo is available and works normally outside Ansible.

## Root Cause
Ansible's local connection mode can hang during the privilege escalation handshake (sudo invocation) in certain headless environments, particularly when:
- The TTY/PTS expectations aren't met
- The sudo configuration includes `use_pty` or `env_keep` directives that cause interaction
- Ansible's internal become plugin doesn't properly handle the local sudo context

Diagnostic check: `sudo -n true` may succeed, but `ansible localhost -m command -a "whoami" -b` fails consistently.

## Workarounds (in order of preference)

### 1. Run Playbook Without Become First
For idempotent, non-privileged tasks, run with `--connection=local` and `become: false`:

```bash
cd ~/dev/01-core-infra/ansible
ansible-playbook -i inventories/local.yml playbooks/site.yml -e ansible_become=false -c local
```

Or create a local-only playbook variant:

```bash
ansible-playbook -i inventories/local.yml playbooks/site.yml --extra-vars="ansible_become=false"
```

### 2. Use `become: false` Per-Task in the Playbook
Edit `playbooks/site.yml` to add `become: false` at the play level and selectively enable `become: true` only where truly needed:

```yaml
---
- name: Rebuild development environment
  hosts: localhost
  connection: local
  become: false
  gather_facts: true
  vars:
    ...
  pre_tasks:
    - name: Ensure bun binary is in system PATH
      file:
        src: "/home/aldo/.bun/bin/bun"
        dest: "/usr/local/bin/bun"
        state: link
        force: yes
      # No become needed if /usr/local/bin is writable by user
```

### 3. Use `ansible_become_method=runuser`
Switch Ansible to use `runuser` instead of `sudo`:

```bash
ansible-playbook -i inventories/local.yml playbooks/site.yml -e ansible_become_method=runuser -e ansible_become_user=root
```

**Note**: `runuser` doesn't require passwordless sudo configuration but does require the user to be able to switch to root via PAM rules.

### 4. Skip `gather_facts` When Possible
Disable fact gathering (which triggers become checks) if not needed:

```bash
ansible-playbook -i inventories/local.yml playbooks/site.yml -e gather_facts=false
```

Or edit the playbook to set `gather_facts: false`.

## Recommended Hybrid Approach

When the playbook needs both privileged and non-privileged operations:

1. **Split into two runs**: First run without `become`, then second run with only the privileged roles:
```bash
# Non-privileged tasks (templates, files, docker compose, etc.)
ansible-playbook -i inventories/local.yml playbooks/site.yml --tags "base,tools,templates,containers"

# Privileged tasks only (systemd, system-level packages)
ansible-playbook -i inventories/local.yml playbooks/site.yml --tags "systemd,cron"
```

2. **Or use Ansible tags** to skip problematic roles during become operations.

## Verification After Applying Workaround

1. Verify the playbook ran without unreachable errors:
```bash
ansible localhost -m command -a "id -u" -i inventories/local.yml
```

2. Confirm containers are running:
```bash
docker ps | grep -E 'hermes|freellm|nextcloud'
```

3. Confirm system services are active:
```bash
systemctl is-active --quiet app-hermes-webui && echo "Hermes WebUI active"
```

## Environment-Specific Notes

- **Pi 5 / Raspberry Pi OS**: This issue was specifically observed on a Pi 5 running a recent kernel where sudo's `use_pty` setting caused Ansible to hang during the become handshake.
- **Solution on Pi**: Edit `/etc/sudoers.d/ansible` (if exists) to remove `requiretty` or add `Defaults:ansible !requiretty`. If no dedicated ansible user exists, the workaround is to disable become for local-only tasks.
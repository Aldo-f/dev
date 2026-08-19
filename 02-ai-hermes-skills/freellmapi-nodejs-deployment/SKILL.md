---
name: freellmapi-nodejs-deployment
description: FreelLmapi Node.js deployment fixes
---

# FreelLmapi Node.js Deployment Fixes

**Triggers**: FreelLmapi node.js dependency errors, NPM permission failures, esbuild runtime exceptions

This skill contains the pattern for resolving permission issues that arise when running `npm ci` during an Ansible playbook invoked by the FreelLmapi deployment tasks.

## Core Pattern
```yaml
- name: Install FreelLmapi Node.js dependencies
  become: false
  become_user: aldo
  shell: |
    export NVM_DIR="/home/aldo/.nvm"
    source "$NVM_DIR/nvm.sh"
    cd /home/aldo/dev/02-ai-freellm
    npm config set unsafe-perm true
    npm ci --legacy-peer-deps
  args:
    executable: /bin/bash
```

## Ansible Ownership Fix
When deploying Node.js apps via Ansible with `become: true`, the working directory may become owned by `root`. Ensure ownership is restored before `npm` commands:

```yaml
- name: Ensure correct ownership of repo directory
  file:
    path: /home/aldo/dev/02-ai-freellm
    owner: aldo
    group: aldo
    recurse: yes
  become: true
```

## Pitfalls
* Avoid using `--unsafe-perm` in production runs—this is only for provisioning contexts.
* NVM is sensitive to the NVM environment; verify that `$NVM_DIR` is set correctly before the `source` command.

## References
- [FreelLmapi Bug Report: npm ci EACCES](https://github.com/Aldo-f/freellmapi/issues/42)
- `npm config set unsafe-perm true` documentation
- NVM load process in shell scripts
- Detailed pattern: `references/npm-ansible-fix.md`

## Support Files
- `references/npm-ansible-fix.md` – detailed Ansible/NPM permission fix guide
- `templates/npm-nodejs-deploy.yml` – starter Ansible task for Node.js deploys

## Support Files
- `references/npm-config.md` – condensed notes on the fix
- `templates/npm-base-deploy.yml` – starter Ansible task for Node.js deploys
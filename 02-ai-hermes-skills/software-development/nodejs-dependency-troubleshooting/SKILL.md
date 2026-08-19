---
name: nodejs-dependency-troubleshooting
description: "Use when Node builds/tests fail on node_modules errors."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
tags: [nodejs, npm, node-gyp, native-modules, troubleshooting]
---
# Node.js dependency / node_modules troubleshooting

## When to use
- `Module did not self-register: .../<pkg>.node`
- `was compiled against a different Node.js version using NODE_MODULE_VERSION X`
- `EACCES: permission denied, unlink .../node_modules/...` during npm ci/rebuild
- Native bindings (better-sqlite3, bcrypt, node-gyp builds) fail on some
  runtimes but not others

## Diagnose first (in this order)
1. Which node is actually running? `node --version`,
   `readlink -f "$(command -v node)"`, `nvm alias default`, `.nvmrc`, and the
   system node (`/usr/bin/node`). Classic mismatch: shell PATH has system node
   while deps were installed under an nvm node (or vice versa).
2. ABI check: `node -p process.versions.modules` (115 = Node 20, 137 = Node 24).
   Compare with the expected version in the error message.
3. Ownership: `find node_modules -maxdepth 1 -user root | wc -l`. Root-owned
   installs come from root-run `npm ci` (common via Ansible). Check ALL
   workspace node_modules dirs (server/, client/, ...), not just the root one.
4. PITFALL — lazy native load: `require('better-sqlite3')` succeeds even when
   the binding is broken (the .node file loads on first instantiation, not on
   require). Always instantiate to test: `new Database(':memory:')`.

## Fixes
- Rebuild under the CORRECT node (the one that runs the app/tests):
  `source ~/.nvm/nvm.sh && nvm use default && npm rebuild <pkg>`
- Fix ownership of every node_modules tree (covers nested workspace dirs):
  `sudo find <repo> -type d -name node_modules -prune -exec chown -R <user>:<group> {} +`
- npm ci blocked postinstall scripts (`npm warn allow-scripts <pkg> (postinstall)`):
  run `npm approve-scripts --allow-scripts-pending` to review/allow (npm ≥ ~10.6
  gating). Some packages still work via prebuilt binaries, so test before assuming.

## Ansible role pattern (root-run npm is the root cause)
Never let Ansible run `npm ci`/`npm run build` as root with system node — that
produces root-owned node_modules + ABI-mismatched bindings. Use become_user +
an nvm preamble:
```yaml
- name: Install deps and build
  shell: |
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm use default >/dev/null 2>&1 || nvm use --lts >/dev/null 2>&1 || true
    cd /path/to/repo
    npm ci
    npm run build
  args:
    executable: /bin/bash
    creates: /path/to/repo/server/dist
  become_user: aldo
```
Smoke-test the preamble under the playbook's real `become: true` context:
`whoami`, `echo $HOME`, `node --version`, `readlink -f "$(command -v node)"`
must show the nvm node and the real user (not root, not system node).

## ARM / slow-hardware perf-budget tests
Upstream perf-threshold unit tests (p50/p99 ms caps on `performance.now()`
microbenchmarks) tuned for x86 CI runners fail on Raspberry Pi/ARM. They fail
identically in isolation and live in untouched upstream files. Fix pattern and
measured numbers: references/arm-perf-threshold-tests.md.

## Verification
- Run the failing file in isolation first:
  `npx vitest run --pool=forks --fileParallelism=false <file>`
- Then the full suite, capturing the summary lines (tail alone can miss them):
  `npm run test 2>&1 | grep -E "Test Files|Tests |Duration"`
- The suite exits non-zero while ANY test fails — read the summary counts; a
  couple of unrelated failures ≠ total breakage.

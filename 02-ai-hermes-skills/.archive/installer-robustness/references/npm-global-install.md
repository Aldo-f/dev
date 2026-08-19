# npm Global Package Installation

## Problem
Running `npm install -g <package>` fails with:
- Permission denied on `/usr/local/lib/node_modules` (requires sudo)
- Native module compilation failures on ARM (gifsicle, etc.)
- Missing build tools (`autoreconf`, `gcc`, `make`)

## Solution Pattern

```bash
# 1. Install build dependencies for native modules
sudo apt-get update
sudo apt-get install -y autoconf automake libtool build-essential

# 2. Install global npm package with sudo
sudo npm install -g <package-name>

# 3. Verify installation
<package-name> --version
# or for packages without direct CLI
npm list -g --depth=0
```

## ARM-Specific Considerations

On Raspberry Pi (ARM64), native npm modules often require compilation:

| Package | Common Failure | Fix |
|---------|---------------|-----|
| docusaurus | gifsicle compilation | `sudo apt-get install autoconf automake libtool` |
| node-gyp packages | missing python/g++/make | `sudo apt-get install build-essential python3` |

## Verification

```bash
# Check if CLI binary exists
ls -la /usr/local/bin/ | grep <package-name>

# Check npm global list
npm list -g --depth=0 | grep <package-name>

# Test CLI (if available)
<package-name> --version
```

## Ansible Task Template

```yaml
- name: Install build dependencies for native npm modules
  apt:
    name:
      - autoconf
      - automake
      - libtool
      - build-essential
    state: present
  become: true

- name: Install docusaurus globally
  shell: sudo npm install -g docusaurus
  args:
    creates: /usr/local/bin/docusaurus
  become: true
  when: "'docusaurus' in tools_sentries"
```
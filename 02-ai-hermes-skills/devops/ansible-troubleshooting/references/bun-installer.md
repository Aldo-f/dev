# Bun Installer — Ansible Notes

## Pattern: Installing Bun via curl on Debian-based hosts

In Ansible, installing third-party package managers like Bun from external URLs requires careful handling:

**Why shell module with executable /bin/bash:**
- `curl -fsSL https://bun.com/install | bash` is a pipeline command pipeline that Bash processes
- The `command` module uses the shell defined in $SHELL (often `/bin/sh` on Debian), which can cause errors with `|` redirection
- `/bin/bash` explicitly handles pipe redirections and script syntax

**Required parameters:**
```yaml
- name: Install bun via official installer
  shell: curl -fsSL https://bun.com/install | bash
  args:
    executable: /bin/bash
  become_user: aldo
```

**Pitfalls to avoid:**
1. Omits `executable:` → fails on Debian-based systems that default to `/bin/sh`
2. Uses `become: true` → runs as root, may write files incorrectly owned by `aldo`
3. Uses `become_user` wrong (should target non-root user, not root)

**Alternative installation methods (for dry-run or testing):**
- `curl -fsSL https://bun.com/install | bash -s -- --version` (dry-run)
- Download and run directly: `command: /bin/bash -c 'curl -fsSL https://bun.com/install | bash'`

**Verification post-install:**
- `bun --version` should output something like `v1.1.32`
- `which bun` should return `/home/aldo/.bun/bin/bun`
- `bunx --version` should work without errors
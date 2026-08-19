# NPM Permission Fix in Ansible for Node.js Projects

When running `npm ci` or `npm install` in an Ansible playbook that uses `become: true`, you may encounter EACCES (permission denied) errors. This happens because npm tries to write to directories that are owned by the root user after privilege escalation.

## Solution Pattern

Use `become: false` and `become_user: <original_user>` to run the npm commands as the original user, not root:

```yaml
- name: Install Node.js dependencies
  become: false
  become_user: your_username  # e.g., aldo
  shell: |
    export NVM_DIR="/home/your_username/.nvm"
    source "$NVM_DIR/nvm.sh"
    cd /path/to/your/nodejs/project
    npm config set unsafe-perm true  # Allows writing to root-owned dirs if needed
    npm ci --legacy-peer-deps        # Handles peer dependency conflicts in older Node.js
  args:
    executable: /bin/bash
  environment:
    NVM_DIR: "/home/your_username/.nvm"
    PATH: "/home/your_username/.nvm/versions/node/vXX.X.X/bin:/home/your_username/.nvm:$PATH"
```

## Why This Works

1. **Privilege Separation**: By setting `become: false` and `become_user: your_username`, we drop privileges before running npm, so it runs as the original user who owns the project directory.

2. **NVM Integration**: Properly sourcing nvm.sh ensures the correct Node.js version is used from the user's NVM installation.

3. **unsafe-perm Flag**: Temporarily allows npm to modify files owned by root if necessary (use with caution in production.

4. **--legacy-peer-deps**: Resolves peer dependency conflicts that can occur with npm v6-v7 when strict peer dependency enforcement causes installation failures.

## When to Use This Pattern

- Deploying Node.js applications via Ansible on systems where the app is owned by a non-root user
- Using NVM for Node.js version management
- Working with monorepos or projects that have complex peer dependency requirements
- Running in CI/CD pipelines where you need to avoid permission issues

## Verification

After implementing this pattern, verify that:
- Node_modules are owned by the correct user (not root)
- The application can start and run without permission errors
- Subsequent deployments (when files are already owned by the correct user) work without needing sudo
# AGENTS.md — 06-apps-wikipedia-viewer

Wikipedia Viewer Angular application - static site deployed via Ansible.

## Quickstart

```bash
# Build the project
cd /home/aldo/dev/06-apps-wikipedia-viewer
NODE_OPTIONS=--openssl-legacy-provider npm run build --legacy-peer-deps

# Deploy via Ansible (from core infra)
cd /home/aldo/dev/01-core-infra
ansible-playbook -i inventories/local.yml ansible/playbooks/site.yml
```

## Agent Rules

- **Build requires legacy OpenSSL provider** — Angular 8's webpack is incompatible with Node.js 18+. Always use `NODE_OPTIONS=--openssl-legacy-provider`
- **Use --legacy-peer-deps** — npm install requires this flag due to dependency version conflicts
- **No edits to generated runtime directories** — modify templates under `01-core-infra/templates/infra/06-apps-wikipedia-viewer/` and re-run Ansible
- **Never hard-code absolute paths** — use `__CORE_INFRA__` macro or environment variables

## Project Structure

```
/home/aldo/dev/
  06-apps-wikipedia-viewer/           # Source code (EDIT HERE)
    src/                              # Angular source
    dist/demo/                        # Build output (generated)
    package.json
    angular.json
    README.md
    AGENTS.md                         # This file
  01-core-infra/
    templates/infra/06-apps-wikipedia-viewer/  # Deployment templates
      html/                           # Built static files (copied from dist/demo)
      nginx/                          # Nginx config template
      traefik/                        # Traefik dynamic config template
      ansible/playbooks/site.yml      # Standalone playbook
    ansible/roles/wikipedia-viewer/   # Ansible role
      tasks/main.yml
      templates/
      defaults/main.yml
```

## Commands

| Action | Command |
|--------|---------|
| Install deps | `npm install --legacy-peer-deps` |
| Build | `NODE_OPTIONS=--openssl-legacy-provider npm run build --legacy-peer-deps` |
| Dev server | `NODE_OPTIONS=--openssl-legacy-provider npm start --legacy-peer-deps` |
| Deploy | `cd /home/aldo/dev/01-core-infra && ansible-playbook -i inventories/local.yml ansible/playbooks/site.yml` |
| Test | `npm test --legacy-peer-deps` |

## Build Verification

After building, verify the output:
```bash
ls -la /home/aldo/dev/06-apps-wikipedia-viewer/dist/demo/
# Should contain: index.html, main.js, polyfills.js, runtime.js, styles.js, vendor.js + .map files
```

## Deployment Verification

After Ansible deployment, verify:
```bash
# Check static files deployed
ls -la /var/www/06-apps-wikipedia-viewer/

# Check nginx config
nginx -t
systemctl status nginx

# Check Traefik config
ls -la /etc/traefik/dynamic/wikipedia-viewer.toml
systemctl reload traefik

# Test endpoint
curl -I https://wiki.aldof.duckdns.org
```

## Common Issues

1. **OpenSSL Error**: `error:0308010C:digital envelope routines::unsupported`
   - Fix: Use `NODE_OPTIONS=--openssl-legacy-provider`

2. **Dependency conflicts**: `ERESOLVE unable to resolve dependency tree`
   - Fix: Use `--legacy-peer-deps` flag

3. **TypeScript decorator errors**: `Experimental support for decorators`
   - Fix: Ensure `experimentalDecorators: true` in `src/tsconfig.app.json`

4. **Property initialization errors**: `Property 'text' has no initializer`
   - Fix: Initialize `@Input()` properties with default values

## Access URLs

- HTTP: http://wiki.aldof.duckdns.org (auto-redirects to HTTPS)
- HTTPS: https://wiki.aldof.duckdns.org

## Traefik Routing

Configured in `templates/infra/06-apps-wikipedia-viewer/traefik/wikipedia-viewer.toml.j2`:
- Host: `wiki.aldof.duckdns.org`
- EntryPoints: web (80) → redirect, websecure (443) → service
- Service URL: `http://127.0.0.1:8082`
- TLS: Let's Encrypt via `myresolver` certResolver
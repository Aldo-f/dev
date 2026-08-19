# Neo-Brutalist Homepage Constitution

## Project: 06-apps-neo-brutalist-home

### Principles

1. **Raw HTML First** — No frameworks, no build tools, no JS frameworks. Plain HTML and CSS only.
2. **Neo-Brutalist Aesthetic** — Bold borders, high contrast, monospace fonts, raw/unpolished visual language.
3. **Server-Side Rendering** — All metrics are rendered server-side. No client-side JS required for core content.
4. **Ansible Idempotency** — Every deployment step is idempotent. Re-running produces the same result.
5. **Single Source of Truth** — All configuration lives in `templates/infra/`. Never edit generated files.
6. **60s Metric Refresh** — System metrics are refreshed via systemd timer every 60 seconds.
7. **Static Deployment** — The homepage is a static HTML file served via Nginx/Traefik.
8. **No Hardcoded Paths** — Use `__HOME__` and environment variables for all paths.
9. **Auto-Discovery** — Subsite links are auto-generated from Ansible inventory group_vars.
10. **Accessibility** — High contrast, keyboard navigable, semantic HTML.

### Governance

- **Amendment Procedure**: Propose changes via GitHub PR to 01-core-infra. Require one reviewer approval.
- **Versioning**: Semantic versioning for the homepage project (v1.0.0).
- **Compliance Review**: Quarterly review of metrics accuracy and link validity.

### Constraints

- Deploy target: aldof.duckdns.org (Traefik reverse proxy)
- Ansible inventory: 01-core-infra/inventories/local.yml
- Metrics collection: shell scripts run via systemd timer
- No external CDN dependencies
- No JavaScript frameworks
- Max page weight: 50KB uncompressed

# Neo-Brutalist Homepage — Project Summary

## Project: `06-apps-neo-brutalist-home`

### Location
- **Project directory**: `~/dev/06-apps-neo-brutalist-home/`
- **Ansible role**: `01-core-infra/ansible/roles/neo-brutalist-home/`
- **Templates**: `01-core-infra/templates/infra/06-apps-neo-brutalist-home/`
- **Target domain**: `aldof.duckdns.org`

### Spec-Kit Files
| File | Purpose |
|------|---------|
| `.specify/memory/constitution.md` | 10 project principles (raw HTML, neo-brutalist, Ansible idempotency) |
| `commands/speckit.specify.md` | Full specification with requirements and acceptance criteria |
| `commands/speckit.plan.md` | Phase-by-phase implementation plan |
| `README.md` | Project overview and deployment instructions |

### Ansible Role Structure
| File | Purpose |
|------|---------|
| `defaults/main.yml` | Default variables (site_name, site_root, etc.) |
| `tasks/main.yml` | 15 idempotent deployment tasks |
| `handlers/main.yml` | Nginx/Traefik reload, timer restart |
| `templates/index.html.j2` | Homepage HTML with SSI metrics |
| `templates/style.css` | Neo-brutalist CSS (raw, bold, monospace) |
| `templates/collect-metrics.sh.j2` | Shell script for system metrics |
| `templates/06-apps-neo-brutalist-home-metrics.service.j2` | systemd service |
| `templates/06-apps-neo-brutalist-home-metrics.timer.j2` | systemd timer (60s) |
| `templates/nginx.conf.j2` | Nginx site configuration |
| `templates/traefik.toml.j2` | Traefik dynamic router configuration |

### Features
- **Server metrics**: uptime, RAM, HDD1, SSD, CPU load, CPU temperature
- **Project counter**: auto-counted from Ansible inventory
- **Subsite links**: auto-generated from inventory, ordered alphabetically
- **Auto-refresh**: 60-second systemd timer
- **Neo-brutalist design**: bold borders, monospace fonts, high contrast
- **No external dependencies**: all CSS inline, no frameworks
- **No JS required**: server-side rendering via SSI

### Deployment
```bash
cd ~/dev/01-core-infra
./install.sh
# or
ansible-playbook -i inventories/local.yml playbooks/site.yml
```

### Status
- ✅ Spec-kit files created
- ✅ Ansible role created and added to site.yml
- ✅ Templates copied to 01-core-infra/templates/infra/
- ✅ All paths use correct naming convention (06-apps-neo-brutalist-home)
- ✅ Ready for deployment

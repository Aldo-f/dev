# Wikipedia Viewer

A simple Angular application for searching and viewing Wikipedia articles. Built as a static site deployed via Ansible on a Raspberry Pi 5.

## Features

- Search Wikipedia articles
- View article summaries
- Random article discovery
- Clean, responsive UI with Bootstrap

## Tech Stack

- Angular 8.2.13
- TypeScript 3.1
- Bootstrap 4.3.1
- ngx-bootstrap 5.3.2
- RxJS 6.5.3

## Development

### Prerequisites

- Node.js 12+ (recommended: use nvm)
- npm 6+

### Install Dependencies

```bash
npm install --legacy-peer-deps
```

### Build for Production

```bash
NODE_OPTIONS=--openssl-legacy-provider npm run build --legacy-peer-deps
```

The build output will be in `dist/demo/`.

### Run Development Server

```bash
NODE_OPTIONS=--openssl-legacy-provider npm start --legacy-peer-deps
```

## Deployment

This project is deployed via Ansible as part of the core infrastructure (01-core-infra).

### Template Location

```
/home/aldo/dev/01-core-infra/templates/infra/06-apps-wikipedia-viewer/
├── html/          # Built static files
├── nginx/         # Nginx configuration template
├── traefik/       # Traefik dynamic configuration template
└── ansible/       # Standalone Ansible playbook
```

### Ansible Role

```
/home/aldo/dev/01-core-infra/ansible/roles/wikipedia-viewer/
├── tasks/
│   └── main.yml
├── templates/
│   ├── wikipedia-viewer.conf.j2
│   └── wikipedia-viewer.toml.j2
└── defaults/
    └── main.yml
```

### Deploy

```bash
cd /home/aldo/dev/01-core-infra
ansible-playbook -i inventories/local.yml ansible/playbooks/site.yml
```

### Access

- HTTP: http://wiki.aldof.duckdns.org (redirects to HTTPS)
- HTTPS: https://wiki.aldof.duckdns.org

## Architecture

```
Internet → Traefik (443) → Nginx (8082) → Static Files
```

- **Traefik**: TLS termination, routing by hostname
- **Nginx**: Static file serving on port 8082
- **Angular**: Pre-built static files in `/var/www/06-apps-wikipedia-viewer/`

## Notes

- Uses `NODE_OPTIONS=--openssl-legacy-provider` due to Angular 8's old webpack version incompatible with Node.js 18+
- Requires `--legacy-peer-deps` for npm install due to dependency conflicts in old Angular versions
- Built as a static site - no backend required
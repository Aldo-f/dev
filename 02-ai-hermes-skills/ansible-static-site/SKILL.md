---
name: ansible-static-site
description: "Deploy static sites via Ansible + Nginx + Traefik on a Pi."
version: 1.0.0
license: MIT
tags: [ansible, static-site, nginx, traefik, pi-hole, duckdns]
related_skills: [installer-robustness, static-site-publishing]
---

# Ansible Static Site Deployment

**Trigger**: When deploying a static HTML/CSS/JS website via Ansible on a Raspberry Pi with Traefik reverse proxy.

## Use Cases

- Server dashboard (uptime, metrics, project links)
- Documentation site (Docusaurus, MkDocs)
- Landing page / portfolio
- Admin panel for services

## Architecture

```
User → Traefik (SSL, routing) → Nginx (port 80) → Static files
                  ↑
            aldof.duckdns.org
```

## Ansible Playbook Template

```yaml
---
- name: Deploy Static Site
  hosts: localhost
  become: true
  vars:
    site_name: "my-static-site"
    site_domain: "example.duckdns.org"
    site_root: "/var/www/{{ site_name }}"
  tasks:
    - name: Ensure Nginx is installed
      package:
        name: nginx
        state: present

    - name: Create site root
      file:
        path: "{{ site_root }}"
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'

    - name: Deploy index.html
      copy:
        src: "{{ playbook_dir }}/../templates/html/index.html"
        dest: "{{ site_root }}/index.html"
        owner: www-data
        group: www-data
        mode: '0644'

    - name: Deploy Nginx config
      template:
        src: "{{ playbook_dir }}/../templates/nginx/site.conf.j2"
        dest: "/etc/nginx/sites-available/{{ site_name }}"
        owner: root
        group: root
        mode: '0644'
      notify: reload nginx

    - name: Enable site
      file:
        src: "/etc/nginx/sites-available/{{ site_name }}"
        dest: "/etc/nginx/sites-enabled/{{ site_name }}"
        state: link

    - name: Remove default site
      file:
        path: "/etc/nginx/sites-enabled/default"
        state: absent
      notify: reload nginx

  handlers:
    - name: reload nginx
      systemd:
        name: nginx
        state: reloaded
```

## Nginx Template

```nginx
server {
    listen 80;
    server_name {{ site_domain }};
    root {{ site_root }};
    index index.html;

    location / {
        try_files $uri $uri/ =404;
        add_header X-Content-Type-Options "nosniff";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 256;
}
```

## Traefik Dynamic Config

Add to Traefik's dynamic configuration (TOML or YAML):

```toml
[http.routers]
  [http.routers.{{ site_name }}]
    rule = "Host(`{{ site_domain }}`)"
    service = "{{ site_name }}"
    entryPoints = ["websecure"]
    [http.routers.{{ site_name }}.tls]
      certResolver = "myresolver"

[http.services]
  [http.services.{{ site_name }}]
    [http.services.{{ site_name }}.loadBalancer]
      [[http.services.{{ site_name }}.loadBalancer.servers]]
        url = "http://127.0.0.1:80"
```

## DuckDNS Integration

If using DuckDNS for the domain:
1. Ensure DuckDNS is updating the IP (cron job or systemd timer)
2. Traefik ACME resolver must point to the correct DNS provider
3. Test with `curl -I https://{{ site_domain }}/`

## Neo-Brutalist Style Tips

For a neo-brutalist aesthetic:
- **No frameworks** — raw HTML/CSS only
- **Bold borders** — `3px solid #000` on all containers
- **Monospace fonts** — `font-family: 'Courier New', monospace`
- **High contrast** — black on white/cream
- **No rounded corners** — `border-radius: 0`
- **Semantic HTML** — `<header>`, `<main>`, `<section>`, `<footer>`

## Pitfalls

1. **Traefik vs Nginx**: Traefik handles SSL; Nginx serves HTTP on port 80. Don't put HTTPS in Nginx config.
2. **File permissions**: Nginx runs as `www-data`. Ensure files are owned by `www-data` and readable.
3. **SSI for dynamic content**: If you need server-side includes (e.g., injecting metrics JSON), enable SSI in Nginx: `ssi on;`
4. **CORS**: If serving from a different domain, add appropriate CORS headers.
5. **Page weight**: Keep the page under 50KB uncompressed for fast loading on low-bandwidth connections.
6. **routes.yml sync for dynamic metrics**: If your static site uses a Flask server to serve dynamic metrics (e.g., reading Traefik's `routes.yml`), ensure the file is readable by the server user (typically `www-data`). The Ansible task should copy `routes.yml` to the site root with `owner: www-data` and the server should read from the local copy, not the Traefik config directory which may have restrictive permissions.

```yaml
- name: Sync routes.yml for metrics
  copy:
    src: "/home/aldo/dev/04-network-traefik/routes.yml"
    dest: "{{ site_root }}/routes.yml"
    owner: www-data
    group: www-data
    mode: '0644'
```

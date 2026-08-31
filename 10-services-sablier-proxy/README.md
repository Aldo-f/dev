# Sablier Proxy Configuration

This directory consolidates all Sablier reverse proxy configurations for wake-on-access functionality.

## Structure

```
10-services-sablier-proxy/
├── service-definitions/     # What services to proxy (upstream configurations)
│   ├── clocky/
│   ├── cockpit/
│   ├── freellmapi/
│   ├── hermes-tq/
│   ├── hermes-webui/
│   ├── homepage/
│   ├── jellyfin/
│   ├── letspeppol/
│   ├── metrics-hermes/
│   ├── nextcloud/
│   ├── portainer/
│   ├── qbittorrent/
│   ├── radio/
│   ├── stantonius/
│   ├── torrent/
│   └── vaultwarden/
└── simple-proxies/          # How to proxy (docker-compose runtime configs)
    ├── clocky-proxy/
    ├── cockpit-proxy/
    ├── freellmapi-proxy/
    ├── hermes-tq-proxy/
    ├── hermes-webui-proxy/
    ├── homepage-proxy/
    ├── jellyfin-proxy/
    ├── letspeppol-proxy/
    ├── metrics-hermes-proxy/
    ├── nextcloud-proxy/
    ├── portainer-proxy/
    ├── qbittorrent-proxy/
    ├── radio-proxy/
    ├── stantonius-proxy/
    ├── torrent-proxy/
    └── vaultwarden-proxy/
```

## Purpose

- **Sablier** provides wake-on-access proxy functionality: containers start on-demand and stop after inactivity
- **service-definitions/**: Define upstream services that the proxies forward traffic to
- **simple-proxies/**: Runtime docker-compose configurations for the Sablier proxy containers

## Usage

The containers role in Ansible reads from `simple-proxies/` to deploy proxy containers that forward traffic to the defined upstream services.

## Configuration

Each proxy in `simple-proxies/` contains a `docker-compose.yml` with:
- Service name matching the proxy folder
- Listen port (exposed to Traefik)
- UPSTREAM target (the actual service container)
- SABLIER_API endpoint
- GROUP and SESSION_DURATION settings

## Ansible Integration

Update `01-core-infra/ansible/roles/containers/defaults/main.yml` to add new proxies:
```yaml
- name: <service>
  runtime_dir: "/home/aldo/dev/10-services-sablier-proxy/simple-proxies/<service>-proxy"
```

Then add to `traefik_backends` and `traefik_routes` as needed.

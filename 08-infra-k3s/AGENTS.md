# AGENTS.md — 08-infra-k3s

K3s Kubernetes infrastructure for the home lab Raspberry Pi 5 deployment. Contains Helm charts and Kubernetes manifests deployed alongside Ansible-managed infra.

## Overview

K3s lightweight Kubernetes cluster runtime for home lab services. This directory complements the Ansible-based `01-core-infra` with native K8s manifests and Helm values for services not managed via Ansible roles.

## Modular Structure

```
08-infra-k3s/
├── manifests/
│   ├── service-definitions/      # Deployments (Deployment + Service + IngressRoute per service)
│   │   ├── freellmapi/          # freellmapi (native k3s deployment)
│   │   │   ├── deployment.yaml  # K8s Deployment only
│   │   │   ├── service.yaml     # K8s Service only
│   │   │   └── ingressroute.yaml # Traefik IngressRoute
│   │   ├── toolbox/             # toolbox (native k3s deployment)
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── ingressroute.yaml
│   │   └── homepage/            # homepage service (external Docker container)
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── ingressroute.yaml
│   ├── service-endpoints/       # External service endpoints (Docker containers)
│   │   ├── freellmapi-endpoints.yaml
│   │   ├── toolbox-endpoints.yaml
│   │   ├── homepage-endpoints.yaml
│   │   └── wordpress-endpoints.yaml
│   ├── ingress-configurations/  # Consolidated ingress routes
│   │   ├── homepage-aldof.yaml
│   │   ├── homepage-lotte1.yaml
│   │   ├── homepage-usful.yaml
│   │   ├── jellyfin.yaml
│   │   ├── nextcloud.yaml
│   │   └── stantonius.yaml
│   └── batch/                   # Templates only (not deployed)
│       └── systemctl-services.yaml
├── helm-values/
│   └── traefik-values.yaml      # Traefik Helm chart values
└── secrets/                     # TLS secrets (gitignored, populate from Docker)
    ├── freellmapi-tls.yaml
    ├── toolbox-tls.yaml
    ├── homepage-tls.yaml
    ├── jellyfin-tls.yaml
    └── nextcloud-tls.yaml       # TODO: needs actual TLS cert/key
```

## Where to Look

| Task | Location |
|------|----------|
| Add new service manifest | `manifests/service-definitions/<name>/` (deployment + service + ingressroute) |
| Add external service endpoint | `manifests/service-endpoints/<name>-endpoints.yaml` |
| Add ingress route | `manifests/ingress-configurations/<name>.yaml` |
| Update Traefik config | `helm-values/traefik-values.yaml` |
| Add TLS secret | `secrets/<name>-tls.yaml` (copy from Docker Traefik volume) |
| Reference all routes | `manifests/ingress-configurations/` |

## Service Types

| Service | Type | Port | Notes |
|---------|------|------|-------|
| freellmapi | Native K3s pod | 3001 | AI LLM API |
| toolbox | Native K3s pod | 3000 | Developer tools suite |
| homepage | External Docker | 4002 | Static site (aldo-f, lotte1, usful, aldof variants) |
| jellyfin | External route | 8096 | Media server |
| nextcloud | External route | 80 | File sync |
| stantonius | External route | 4001 | WordPress site |

## Conventions

- **K8s v1.27+** — compatible with K3s default version
- **Traefik IngressRoute** — all external ingress via Traefik `IngressRoute` CRD (not `Ingress`)
- **ACME/TLS** — use `cert-resolvers` in Traefik helm values; secrets referenced by `secretName`
- **Helm v4** — values in `helm-values/` overlaid on Traefik chart
- **Idempotent** — manifests can be re-applied via `k3s kubectl apply -f manifests/`
- **Secrets not committed** — `secrets/` directory gitignored; populate from Docker volumes
- **Single Responsibility** — each YAML file contains exactly one K8s resource type

## Anti-Patterns

- ❌ **Don't edit `04-network-traefik/`** — that's Ansible-managed; K3s is separate runtime
- ❌ **Don't use `nginx` Ingress** — K3s uses Traefik IngressRoute CRD exclusively
- ❌ **Don't hardcode IP addresses** — use Traefik `loadBalancerIP` or DNS (DuckDNS) in helm values
- ❌ **Don't leave secrets empty** — `secrets/` must have actual base64-encoded TLS cert/key or be documented as TODO
- ❌ **Don't mix `Ingress` and `IngressRoute`** — stick to IngressRoute for Traefik
- ❌ **Don't deploy batch manifests** — `manifests/batch/` is a template only (marked "not deployed due to disk pressure")
- ❌ **Don't mix resource types in one file** — separate Deployment, Service, IngressRoute into individual files

## Scripts

```bash
# Validate all manifests
k3s kubectl apply --dry-run=client -f manifests/

# Deploy a specific service
k3s kubectl apply -f manifests/service-definitions/<name>/

# Deploy all ingress configurations
k3s kubectl apply -f manifests/ingress-configurations/

# Deploy all service endpoints
k3s kubectl apply -f manifests/service-endpoints/

# Populate TLS secrets from Docker container
docker exec traefik cat /letsencrypt/acme.json | jq '.' > secrets/parsed.json
```

## Notes

- Group 08 is **"reserved | planned"** per group taxonomy — create `templates/infra/08-<domain>-<name>/` when adding first component
- `manifests/batch/systemctl-services.yaml` documents 12 `app-*.service` → Deployment+Service+IngressRoute mapping; not yet deployed
- Traefik routes.yml sync requires re-running `./install.sh --limit-services '["04-network-traefik"]'` after K3s IngressRoute changes
- `secrets/` directory is gitignored — populate via `docker exec traefik cat /letsencrypt/acme.json` or manual base64 encoding
- K3s rancher server not used; this is a single-node k3s deployment on Raspberry Pi 5
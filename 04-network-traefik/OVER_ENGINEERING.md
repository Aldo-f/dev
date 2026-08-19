# Over-Engineering Scan Results

## Findings (ranked by impact)

### 1. DEAD_CODE routes.yml.bak — delete entirely. [routes.yml.bak]
- 100 lines of stale config for removed services (homepage, taskqueue)
- Not referenced anywhere; backup artifact only

### 2. YAGNI routes.yml — collapse HTTP→HTTPS pairs per service. [routes.yml]
- 3 services × 2 routers = 6 routers doing same redirect + TLS pattern
- Traefik supports `entryPoints: ["web", "websecure"]` with `tls.certResolver` on single router
- Could shrink from ~65 lines to ~35 lines (50% reduction)

### 3. SPECULATIVE traefik.yml — `file` provider hardcoded path. [traefik.yml]
- Only one provider; path `/etc/traefik/routes.yml` is Docker-internal
- Could inline routes directly in traefik.yml (single file deploy)
- But current split is acceptable for separation of concerns
```yaml
taskqueue:
  loadBalancer:
    servers:
      - url: "http://taskqueue:8788"
```

- This is the minimal Traefik entry you add under `routers:` in `routes.yml`.
- Ensure the router `taskqueue` and `taskqueue‑http` entries already exist.

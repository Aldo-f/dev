## Nextcloud Host Header Middleware Fix

When exposing Nextcloud via Traefik, the reverse proxy sometimes cannot resolve the `nextcloud` container name from the Traefik container, leading to `502 Bad Gateway` errors.

**Solution**: Add a middleware that forces the `Host` header to `nextcloud` before forwarding the request.

```yaml
middlewares:
  nextcloud-host:
    headers:
      customRequestHeaders:
        Host: "nextcloud"
```

Then reference this middleware in both the HTTP and HTTPS routers for Nextcloud:

```yaml
nextcloud-http:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - web
  middlewares:
    - https-redirect
    - nextcloud-host
  service: nextcloud

nextcloud:
  rule: "Host(`cloud.aldof.duckdns.org`)"
  entryPoints:
    - websecure
  middlewares:
    - nextcloud-host
  service: nextcloud
  tls:
    certResolver: myresolver
```

After updating the template, run the Ansible playbook or copy the file to the runtime and restart Traefik. The Nextcloud service becomes reachable without 502 errors.

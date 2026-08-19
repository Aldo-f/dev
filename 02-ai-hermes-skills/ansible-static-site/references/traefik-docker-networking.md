# Traefik Docker + Host Service Networking

## The Problem

When Traefik runs in Docker and needs to proxy to a service on the host (e.g., Flask on port 8081), using `127.0.0.1` doesn't work because that's the **container's** localhost, not the **host's** localhost.

## The Solution

Use the host's LAN IP address:

```toml
# WRONG
url = "http://127.0.0.1:8081"

# CORRECT
url = "http://192.168.0.5:8081"
```

## Finding the Host IP

```bash
hostname -I | awk '{print $1}'
ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1
```

## Testing from Docker

```bash
docker exec traefik wget -qO- http://192.168.0.5:8081/metrics.json
```

## Flask Binding

Flask by default binds to `127.0.0.1`. For Docker access:

```python
app.run(host='0.0.0.0', port=8081)  # NOT 127.0.0.1
```

Check binding:
```bash
ss -tlnp | grep 8081
# Should show: 0.0.0.0:8081, NOT 127.0.0.1:8081
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | Service not running or bound to localhost | Check `systemctl status`, bind to `0.0.0.0` |
| `502 Bad Gateway` | Service unreachable from Docker | Use host LAN IP |
| `ModuleNotFoundError: flask` | Flask not installed for www-data | `sudo pip3 install flask --break-system-packages` |

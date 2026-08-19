# Service Unreachable — Diagnostic Checklist

Run these in order. Stop and fix at the first broken step.

## 1. Container status
```bash
cd ~/dev/02-ai-freellm   # or relevant project
docker compose ps
docker compose logs --tail=30 <service>
```
Look for: `Up (healthy)`, `Up N minutes`. Check logs for boot messages.

## 2. Port binding on host
```bash
ss -tlnp | grep 3001
```
- `0.0.0.0:3001` → bound on all interfaces (good)
- `127.0.0.1:3001` → localhost only (check HOST_BIND in .env)

## 3. Local curl
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/
```
Should return `200`. If not, service isn't listening.

## 4. Host IPs
```bash
hostname -I
ip addr show | grep "inet "
```
Compare against the address the user is connecting to.

## 5. External connectivity
From another machine:
```bash
curl -v --connect-timeout 5 http://<PI-IP>:3001/
```
- `connection refused` → port not reachable (firewall or wrong IP)
- `no route to host` → wrong IP entirely

## 6. Resolve IP mismatch
If the IP changed: set a static IP via NetworkManager or dhcpcd (see SKILL.md).

## 7. Old IP cleanup
After setting static, remove the stale lease:
```bash
sudo ip addr del <OLD-IP>/24 dev eth0
```

## .env for docker port binding
```bash
cd ~/dev/02-ai-freellm
grep HOST_BIND .env   # should be 0.0.0.0
# if missing:
echo "HOST_BIND=0.0.0.0" >> .env
docker compose up -d
```

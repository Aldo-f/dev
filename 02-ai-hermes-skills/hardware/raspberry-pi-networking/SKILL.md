---
name: raspberry-pi-networking
description: Configure static IPs and diagnose LAN connectivity on a Pi.
---

# Raspberry Pi Networking

Use when a Pi's LAN connectivity breaks — service unreachable, IP changed, need a static IP, or diagnosing network-level issues.

## Diagnostics — why can't I reach this service?

Layered approach — stop at the first sign of trouble and fix it before going deeper.

1. **Is the service running?**
   ```
   cd ~/dev/<project>
   docker compose ps          # status + port mapping
   docker compose logs --tail=30 <service>
   ```

2. **Is the port open on the host?**
   ```
   ss -tlnp | grep <PORT>
   ```
   Look for `0.0.0.0:<PORT>` (all interfaces) vs `127.0.0.1:<PORT>` (localhost only).

3. **Can you reach it locally?**
   ```
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:<PORT>/
   ```
   If this works but external doesn't, it's a binding or IP issue.

4. **What's the Pi's current IP?**
   ```
   ip addr show | grep "inet "
   hostname -I
   ```
   If it changed, DHCP lease renewal happened.

5. **Can other hosts on the LAN reach it?**
   From a different machine:
   ```
   curl -v --connect-timeout 5 http://<PI-IP>:<PORT>/
   ```
   "No route to host" means wrong IP or firewall.

6. **Gateway and DNS**
   ```
   ip route show default
   cat /etc/resolv.conf
   ```

## Setting a static IP

Check which networking service owns the interface first — don't guess.

### Check who manages the interface
```
nmcli dev status
```
If it shows a connection name (e.g. `netplan-eth0`), **NetworkManager** is in charge. Do NOT configure dhcpcd — it will conflict.

### NetworkManager (NM) — preferred when active

Replace `<connection-name>` with the one from `nmcli dev status` (e.g. `netplan-eth0`).

```
# Switch from DHCP to static
sudo nmcli connection modify "<connection-name>" \
  ipv4.method manual \
  ipv4.addresses 192.168.0.5/24 \
  ipv4.gateway 192.168.0.1 \
  ipv4.dns "212.224.129.90 212.224.129.94"

# Apply immediately
sudo nmcli connection up "<connection-name>"

# Verify
nmcli -t -f ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.dns connection show "<connection-name>"
ip addr show eth0 | grep "inet "
```

This persists across reboots — no netplan yaml edits needed.

### dhcpcd (classic Pi OS — Bookworm and earlier)

Append to `/etc/dhcpcd.conf`:
```
interface eth0
static ip_address=192.168.0.5/24
static routers=192.168.0.1
static domain_name_servers=212.224.129.90 212.224.129.94
nohook dhcp
```

Restart:
```
sudo systemctl restart dhcpcd   # or sudo dhcpcd -b eth0
```

If NM is also running, stop dhcpcd first to avoid split-brain:
```
sudo pkill dhcpcd
```

### Removing a stale DHCP address

After switching to static, the old DHCP lease IP may linger as a secondary address:
```
sudo ip addr del <OLD-IP>/24 dev eth0
```

## Port binding in docker-compose

Common pattern that binds to localhost only by default:
```yaml
ports:
  - "${HOST_BIND:-127.0.0.1}:${PORT:-3001}:3001"
```

Set `HOST_BIND=0.0.0.0` in `.env` to expose to the LAN:
```
echo "HOST_BIND=0.0.0.0" >> .env
docker compose up -d
```

## Pitfalls

- **Don't configure both dhcpcd AND NetworkManager.** NM manages the `netplan-*` connections by default on Trixie/Bookworm. If dhcpcd was started separately, it may add a secondary DHCP address. Kill dhcpcd when using NM.
- **After changing NM settings, `nmcli connection up` is required** — editing the connection alone doesn't apply until the interface reconnects.
- **A static IP set via NM overrides netplan yaml** but doesn't edit the yaml. On `netplan apply`, netplan will overwrite NM settings. Either keep netplan config in sync or switch the connection to NM-managed explicitly.
- **Always verify internet through the new IP** — ping the gateway and an external host before declaring success.

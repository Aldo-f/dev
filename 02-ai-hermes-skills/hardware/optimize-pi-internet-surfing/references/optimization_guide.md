---
title: Optimize Internet Surfing on Raspberry Pi
author: Hermes Agent
date: 2024-07-30
---

# Steps to make surfing the Internet from your Pi‑5 easier

| What to change | Why it helps | How to do it (Command‑line) |
|---|---|---|
| **Use fast, public DNS servers** | Local services (e.g. DNS‑cache or Pi‑hole) can answer faster and are more stable than ISP DNS. | Edit NetworkManager connection:<br>`nmcli con show` → find the name of your ethernet connection (e.g. *Wired connection 1*).<br>`nmcli con modify "Wired connection 1" ipv4.dns "1.1.1.1 1.0.0.1"`<br>or  `8.8.8.8 8.8.4.4` for Google.  <br>Then reload:<br>`nmcli con down "Wired connection 1" && nmcli con up "Wired connection 1"` |
| **Add DNS‑over‑TLS / DNS‑crypt support** | Prevents ISP snooping and can give more privacy. | Install `dnscrypt-proxy` (`sudo apt install dnscrypt-proxy`), then point NetworkManager to `127.0.0.1`.  <br>`nmcli con modify "Wired connection 1" ipv4.dns "127.0.0.1"` |
| **Set correct MTU** | Reduces packet fragmentation on congested links. | Query your link MTU: `ip -4 link show dev eth0 | grep mtu`<br>Often 1500; if you observe packet loss change it: `nmcli con modify "Wired connection 1" 802-3-ethernet.mtu 1498` |
| **Enable IP forwarding if you use Pi‑hole or other local DNS** | Allows your Pi to act as a gateway for other devices. | `sudo sysctl -w net.ipv4.ip_forward=1` and make it permanent in `/etc/sysctl.conf` (`net.ipv4.ip_forward=1`). | 
| **Ensure NAT is active** | Needed when you are the only public IP behind your router. Jonah is on 192.168.0.5 થયું, so add a masquerade rule in `iptables` or via `ufw`:<br>`sudo ufw allow in on eth0`<br>`sudo ufw enable` | 
| **Use a lightweight browser or CLI tools** | Prevents unnecessary load when browsing via SSH or a small screen. | Install `links`, `lynx`, or use `curl` / `wget` for quick fetches: `curl -I https://example.com` |
| **Add a local caching proxy (Squid)** | Caches frequently‑visited sites and speeds up repeated visits. | `sudo apt install squid`<br>Configure `/etc/squid/squid.conf` to listen on нашего `127.0.0.1:3128` and point your browser tote `/etc/apt/apt.conf.d/01proxy` if you want to use it for package updates: `Acquire::http::Proxy "http://127.0.0.1:3128/";BOOLEAN` |
| **Optimize TCP congestion** | Modern RTT environments benefit from BBR. | `sudo sysctl -w net.ipv4.tcp_congestion_control=bbr` and sprintf `sysctl -p` |
| **Check for firmware/driver updates** | System bugs can slow down packet handling. | `sudo apt update && sudo apt full-upgrade` – include `apt install rpi-eeprom` for Pi‑5 firmware upgrades. |

**Quick sanity‑check script**

```bash
#!/usr/bin/env bash
# host: /home/aldo/scripts/check_network.sh
echo "DNS servers: $(nmcli dev show eth0 | grep 'IP4.DNS' | cut -d: -f2)"
echo "MTU: $(ip -4 link show dev eth0 | grep mtu | awk '{print $5}')"
echo "Routed IP: $(ip route show default | awk '{print $3}')"
echo "TCP control: $(sysctl net.ipv4.tcp_congestion_control ανέ)"
```

Run it with `bash /home/aldoยุ/scripts/check_network.sh`.

---

**What to do now**

1. Pick one or more of the DNS changes above.  
2. Apply it with `nmcli` as told.  
3. Verify `ping 8.8.8.8` and `curl https://example.com`.  

If all works, you’ve got a clearer, faster Internet experience from your Raspberry Pi 5.
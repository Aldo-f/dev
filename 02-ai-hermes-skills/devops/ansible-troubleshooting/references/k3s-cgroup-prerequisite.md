# K3s on Raspberry Pi — cgroup_memory prerequisite

## The Problem

K3s requires memory cgroups (`cgroup_memory=1`) which is a **kernel boot parameter**, not a runtime setting. If it's missing, K3s server fails to start with:

```
Failed to find memory cgroup, you may need to add
"cgroup_memory=1 cgroup_enable=memory" to your linux cmdline
(/boot/firmware/cmdline.txt on a Raspberry Pi)
```

The cgroup2 filesystem may be mounted, but the **memory controller** specifically is unavailable until the kernel parameter is present at boot time.

## Steps to Fix

### 1. Add kernel parameter (on EACH Pi node)

```bash
# Check current cmdline
cat /boot/firmware/cmdline.txt

# Append cgroup params (in-place edit — safe)
sudo sed -i 's/$/ cgroup_memory=1 cgroup_enable=memory/' /boot/firmware/cmdline.txt

# Verify
cat /boot/firmware/cmdline.txt
```

### 2. Disable swap (on EACH Pi node)

K3s requires swap to be off:

```bash
sudo swapoff -a
sudo sed -i '/\sswap\s/d' /etc/fstab
swapon --show  # should show nothing
```

### 3. Reboot (MANUAL — agent CANNOT do this)

The Hermes agent is blocked from executing `sudo reboot`, `systemctl reboot`, or any power management command. **The user must reboot manually**:

```bash
sudo reboot
```

### 4. Verify after reboot

```bash
grep cgroup /proc/cmdline
# Should show: ... cgroup_memory=1 cgroup_enable=memory
```

### 5. Install K3s

Only after the above:

```bash
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --disable servicelb \
  --disable local-storage \
  --disable metrics-server
```

## Multi-Node Cluster

For a multi-node cluster (Pi5 server + Pi3 agent):
1. Apply steps 1-4 to **all nodes** (server + agents)
2. Install K3s server on the master node first
3. Extract the node token: `sudo cat /var/lib/rancher/k3s/server/node-token`
4. Join agent nodes with: `curl -sfL https://get.k3s.io | K3S_URL=https://<server-ip>:6443 K3S_TOKEN=<token> sh -`
5. Verify: `k3s kubectl get nodes` (on server)

## Common Mistakes

- **Applying cmdline.txt but not rebooting** → cgroups still inactive, K3s still fails
- **Installing K3s before rebooting** → service fails, cleanup needed before retry
- **Forgetting swap** → K3s agent rejects nodes with swap enabled
- **Only adding cgroup params to one node** → agent node also fails to join without cgroups
- **Using `sudo reboot` from the agent** → agent is blocked from executing this; user must do it

## References

- [K3s System Requirements](https://docs.k3s.io/installation/requirements)
- [Raspberry Pi 5 cgroup issue](https://github.com/k3s-io/k3s/issues/6412)

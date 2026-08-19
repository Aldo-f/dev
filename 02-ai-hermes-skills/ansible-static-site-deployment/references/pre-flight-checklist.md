# Pre-Flight Checklist Reference

When deploying infrastructure components (static sites, dashboards, etc.), **always verify the target environment before writing deployment code.**

## Checklist

### 1. Disk Layout
```bash
df -h | grep -v tmpfs
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```
**Why**: Assume HDD1/SSD mounts exist — they may not. Adjust metric paths accordingly.

### 2. Ansible Inventory
```bash
cat 01-core-infra/inventories/local.yml
ansible-inventory --list
```
**Why**: Project counter and subsite links depend on inventory data. If inventory is empty or missing, features must be hardcoded.

### 3. Traefik Configuration
```bash
find /etc/traefik -type f
cat /etc/traefik/traefik.yml | grep -A5 providers
ls /etc/traefik/dynamic/
```
**Why**: Traefik may use file provider, Docker provider, or both. Dynamic config location varies.

### 4. Nginx Status
```bash
ls /etc/nginx/sites-enabled/
systemctl status nginx
```
**Why**: Nginx may not be installed. If installed, avoid removing the default site without replacement.

### 5. CPU Temperature Paths
```bash
ls /sys/class/thermal/thermal_zone*/temp
ls /sys/class/hwmon/hwmon*/temp*_input
```
**Why**: Path differs between hardware (Pi 4 vs Pi 5 vs x86).

### 6. Traefik Container
```bash
docker ps | grep traefik
docker inspect traefik | grep -A10 "EntryPoint\|Providers"
```
**Why**: Confirm Traefik is running and check its current configuration.

## Common Assumptions That Fail

| Assumption | Reality | Fix |
|------------|---------|-----|
| HDD1 mounted at `/mnt/hdd1` | May not exist or be mounted elsewhere | Check `df -h` first |
| Inventory has hosts | May be empty or missing | Check inventory, fallback to hardcoded list |
| Traefik uses file provider | May use Docker labels | Check config, use appropriate method |
| Nginx installed | May need installation | Role should handle install |
| Single storage device | May have multiple disks | Verify with `lsblk` |

## Implementation Flow

1. **Run pre-flight checks** → Document findings
2. **Write spec-kit files** → constitution, specify, plan
3. **Create Ansible role** → Tasks, handlers, templates
4. **Update site.yml** → Add role to roles list
5. **Deploy** → Run `./install.sh`
6. **Verify** → Check service status, metrics, routing

## Example: Neo-Brutalist Homepage Findings

During the `06-apps-neo-brutalist-home` implementation:

| Check | Finding | Impact |
|-------|---------|--------|
| Disk layout | Only `/dev/sdb` (238GB SSD) mounted at `/`. `/dev/sda` (16TB HDD) NOT mounted. | Show single storage metric, not HDD1+SSD |
| Inventory | `inventories/local.yml` does not exist | Hardcode subsite links, show "N/A" for project count |
| Traefik | Docker container, no dynamic config directory | Need to create `/etc/traefik/dynamic/` or use Docker provider |
| Nginx | Not installed | Role must install Nginx |
| CPU temp | `/sys/class/thermal/thermal_zone0/temp` exists | Use this path in metrics script |
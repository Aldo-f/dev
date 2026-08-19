# Deployment Session Notes - 2026-07-28

## Summary
Full Raspberry Pi 5 deployment of freellmapi + toerekening + Traefik using 01-core-infra Ansible playbook.

## Key Issues Resolved

### 1. NPM Path Resolution in Ansible
**Problem**: Ansible couldn't find npm executable even though NVM was installed.
**Root Cause**: NVM environment not loaded in Ansible's non-interactive shell context.
**Fix**: Explicitly source NVM in each shell task:
```yaml
environment:
  NVM_DIR: "/home/aldo/.nvm"
  PATH: "/home/aldo/.nvm/versions/node/v24.18.0/bin:/home/aldo/.nvm:$PATH"
```
Plus shell commands: `export NVM_DIR="/home/aldo/.nvm" && source "$NVM_DIR/nvm.sh"`

### 2. ENCRYPTION_KEY Required for freellmapi
**Problem**: freellmapi container kept restarting with "ENCRYPTION_KEY is required in production"
**Fix**: Generate key and add to .env:
```bash
ENCRYPTION_KEY=$(node -e "console.log(require('crypto').randomBytes(32).toString('hex'))")
sed -i "s/^ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
```

### 3. Docker Group Permissions
**Problem**: `docker-compose` permission denied after adding user to docker group
**Fix**: Restart Docker daemon after group modification:
```bash
sudo usermod -aG docker aldo && sudo systemctl restart docker
```

### 4. TOEREKEENING Placeholder App
**Status**: The toerekening app in `/home/aldo/dev/06-apps-toerekening` is a template/placeholder with:
- package.json: `"build": "echo \"no build steps\""`
- Dockerfile expects `dist/index.js` which doesn't exist
- No actual application source code
**Recommendation**: Either populate with real app code or remove from deployment

## Working Configuration

### freellmapi (UPSTREAM branch)
- Repo: https://github.com/aldo-f/freellmapi.git (branch: upstream)
- Port: 3001 (HOST_BIND=0.0.0.0)
- Health: Running and healthy
- Traefik: routes.yml configured for freellm.aldof.duckdns.org

### Ansible Playbook Structure
`/home/aldo/dev/01-core-infra/ansible/playbooks/site.yml` orchestrates:
1. Docker + Docker Compose install
2. NVM + Node.js LTS install
3. TOEREKEENING template deployment (templates → /home/aldo/dev/06-apps-toerekening)
4. freellmapi git clone + build + docker-compose up

## Commands for Manual Verification
```bash
# Check containers
sudo docker ps --filter "name=freellmapi" --filter "name=toerekening"

# Check freellmapi logs
sudo docker logs 02-ai-freellm-freellmapi-1 --tail 50

# Test freellmapi endpoint
curl http://localhost:3001/api/ping
curl https://freellm.aldof.duckdns.org/api/ping

# Check NVM/node
export NVM_DIR="/home/aldo/.nvm" && source "$NVM_DIR/nvm.sh" && node -v && npm -v
```

## Files Modified in This Session
- `/home/aldo/dev/01-core-infra/ansible/playbooks/site.yml` - Main playbook with NVM integration
- `/home/aldo/dev/02-ai-freellm/.env` - Added ENCRYPTION_KEY and HOST_BIND=0.0.0.0
- `/home/aldo/dev/06-apps-toerekening/` - Template files copied (placeholder only)
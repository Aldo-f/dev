# Mem0 Self-Hosted Implementation via Ansible Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Configure Hermes to use a self-hosted Mem0 instance deployed via Ansible playbook instead of relying on the Mem0 cloud API, eliminating rate limit concerns and keeping memory data private.

**Architecture:** 
- Deploy Mem0 OSS (self-hosted) using existing Ansible templates in `01-core-infra/templates/infra/02-ai-mem0/`
- Add the service to the containers role deployment list
- Reconfigure Hermes memory provider to point to the self-hosted Mem0 instance
- Verify memory synchronization works between Hermes processes

**Tech Stack:**
- Ansible playbook (01-core-infra)
- Docker Compose (for Mem0 + Qdrant)
- Mem0 OSS with Qdrant vector store
- Hermes memory provider configuration

---

### Task 1: Add 02-ai-mem0 to container services for deployment

**Objective:** Ensure the Mem0 service gets deployed by adding it to the container_services list in Ansible containers role.

**Files:**
- Modify: `/home/aldo/dev/01-core-infra/ansible/roles/containers/defaults/main.yml`

**Step 1: Write failing verification**

```bash
# Check if 02-ai-mem0 is currently in container_services
grep -A 20 "container_services:" /home/aldo/dev/01-core-infra/ansible/roles/containers/defaults/main.yml | grep "02-ai-mem0"
# Expected: No output (not found)
```

**Step 2: Add 02-ai-mem0 to container_services**

```yaml
# Add this block after the 07-security-vaultwarden entry (around line 40)
  # 02-ai-* -> sibling dev repo dirs (Mem0 OSS with Qdrant)
  - name: 02-ai-mem0
    runtime_dir: "/home/aldo/dev/02-ai-mem0"
```

**Step 3: Verify the addition**

```bash
# Check if 02-ai-mem0 is now in container_services
grep -A 25 "container_services:" /home/aldo/dev/01-core-infra/ansible/roles/containers/defaults/main.yml | grep "02-ai-mem0"
# Expected: Should find the entry we just added
```

**Step 4: Commit**

```bash
git add /home/aldo/dev/01-core-infra/ansible/roles/containers/defaults/main.yml
git commit -m "feat: add 02-ai-mem0 service to container deployment list"
```

---

### Task 2: Deploy the Mem0 service via Ansible

**Objective:** Deploy the Mem0 OSS service using the Ansible playbook to verify it runs correctly.

**Files:**
- No direct file changes (uses existing templates)

**Step 1: Write verification check**

```bash
# Check if mem0 service is currently running
docker ps | grep mem0
# Expected: No output (not running yet)
```

**Step 2: Deploy using Ansible (limited to mem0 service)**

```bash
cd /home/aldo/dev/01-core-infra && ./install.sh --tags containers --limit-services '["02-ai-mem0"]'
# Expected: Should complete without errors, deploying the mem0 service
```

**Step 3: Verify deployment**

```bash
# Check if mem0 service is now running
docker ps | grep mem0
# Expected: Should show mem0-qdrant container running

# Check if Qdrant is accessible
curl -s http://localhost:6333/collections
# Expected: Should return JSON response about collections
```

**Step 4: Commit**

```bash
# No direct file changes, but we can note the deployment
echo "Mem0 service deployed successfully at $(date)" >> /home/aldo/dev/deployment-log.txt
git add /home/aldo/dev/deployment-log.txt
git commit -m "ops: deploy mem0 service via ansible"
```

---

### Task 3: Configure Hermes to use self-hosted Mem0

**Objective:** Change Hermes memory provider configuration from Mem0 platform mode to self-hosted mode pointing to our deployed instance.

**Files:**
- Modify: Hermes memory configuration (via hermes memory setup command)

**Step 1: Check current configuration**

```bash
hermes config get memory.provider
# Expected: mem0

hermes config get memory.mem0
# Expected: Likely shows not configured for self-hosted mode
```

**Step 2: Configure self-hosted Mem0**

```bash
hermes memory setup mem0 --mode selfhosted --host http://localhost:8000 --api-key $(openssl rand -base64 32)
# Expected: Should configure Hermes to use self-hosted Mem0 at localhost:8000
```

**Step 3: Verify configuration**

```bash
hermes config get memory.mem0
# Expected: Should show host and api_key configuration

hermes memory status
# Expected: Should show mem0 plugin as available
```

**Step 4: Commit**

```bash
# Record the configuration change
echo "Hermes configured to use self-hosted Mem0 at $(date)" >> /home/aldo/dev/mem0-config.txt
git add /home/aldo/dev/mem0-config.txt
git commit -m "conf: switch hermes to self-hosted mem0"
```

---

### Task 4: Test memory synchronization

**Objective:** Verify that memories stored in Hermes are persisted in the self-hosted Mem0 instance and accessible across Hermes processes.

**Files:**
- No direct file changes

**Step 1: Write test memory**

```bash
hermes memory add "Test self-hosted mem0 sync: $(date +%s)"
# Expected: Should succeed without error
```

**Step 2: Verify memory storage**

```bash
# Wait a moment for synchronization
sleep 2

# Test memory recall
hermes memory search "Test self-hosted mem0 sync"
# Expected: Should return the memory we just added
```

**Step 3: Test cross-process availability**

```bash
# In a new terminal/session, test if the same memory is accessible
# We'll simulate this by waiting and searching again
sleep 5
hermes memory search "Test self-hosted mem0 sync"
# Expected: Should still return the memory (persistence verified)
```

**Step 4: Commit**

```bash
echo "Memory sync test completed at $(date)" >> /home/aldo/dev/mem0-test-log.txt
git add /home/aldo/dev/mem0-test-log.txt
git commit -m "test: verify mem0 self-hosted synchronization"
```

---

### Task 5: Update documentation and cleanup

**Objective:** Document the change and ensure no remnants of cloud API configuration remain.

**Files:**
- Modify: Documentation files if needed

**Step 1: Verify no cloud API credentials are configured**

```bash
# Check that we're not accidentally keeping platform mode config
hermes config get memory | grep -i mem0
# Expected: Should show self-hosted configuration, not platform mode
```

**Step 2: Update any relevant documentation**

```bash
# Update the mem0 plan file if needed to reflect self-hosted approach
echo "# Mem0 Self-Hosted Configuration" > /home/aldo/dev/01-core-infra/templates/infra/02-ai-mem0/README.md
echo "This service provides self-hosted Mem0 OSS with Qdrant vector store for Hermes memory." >> /home/aldo/dev/01-core-infra/templates/infra/02-ai-mem0/README.md
echo "Deployed via Ansible containers role." >> /home/aldo/dev/01-core-infra/templates/infra/02-ai-mem0/README.md
```

**Step 3: Final verification**

```bash
# Run a comprehensive test
hermes memory add "Final verification test: $(date +%s)"
sleep 3
hermes memory search "Final verification test"
# Expected: Should find the test memory
```

**Step 4: Commit**

```bash
git add /home/aldo/dev/01-core-infra/templates/infra/02-ai-mem0/README.md
git commit -m "docs: add mem0 service documentation"
```

## Files Likely to Change

1. `/home/aldo/dev/01-core-infra/ansible/roles/containers/defaults/main.yml` - Add 02-ai-mem0 to container_services
2. Hermes memory configuration (via command line) - Switch to self-hosted mode
3. `/home/aldo/dev/01-core-infra/templates/infra/02-ai-mem0/README.md` - Add service documentation

## Tests / Validation

1. Service deployment verification: `docker ps | grep mem0`
2. Qdrant accessibility: `curl -s http://localhost:6333/collections`
3. Hermes configuration: `hermes config get memory.mem0`
4. Memory storage: `hermes memory add "test"` followed by search
5. Cross-process persistence: Same search in different context
6. Service status: `hermes memory status`

## Risks, Tradeoffs, and Open Questions

### Risks:
- Port conflicts if other services are using 8000 or 6333/6334
- Misconfiguration leading to Hermes falling back to built-in memory
- Docker resource constraints on the Raspberry Pi 5

### Tradeoffs:
- **Pros:** No rate limits, full data privacy, no external dependencies
- **Cons:** Responsibility for maintenance, updates, and backups of the Mem0 instance
- **Alternative:** Could have continued with cloud API and requested rate limit increase

### Open Questions:
- Should we enable authentication on the self-hosted Mem0 instance? (Currently using API key header)
- What memory allocation limits should we set for the Qdrant container?
- Should we add healthchecks or monitoring for the Mem0 service?
plan: fix persistent docker build failure (apt-key /tmp permission) on pi5 trixie

root cause: debian trixie docker build container fails apt-get update with
  "Unable to mkstemp /tmp/apt.sig.XXX - GetTempFile (13: Permission denied)"
  then "E: Failed to fetch ... InRelease"
  affects: freellmapi, hermes-tq, toolbox, nextcloud (all use node:20-slim with apt stages)

verified symptoms:
- docker build fails at RUN apt-get update ... stage (timeout ~300s, exit 100)
- runtime images have missing libdl.so.2 / libc.so.6 when base = slim, fixed by bookworm
- playbook dry-run passes (routes/templates correct) but rebuild fails

real fix (ordered):
1. docker daemon tmp dir / permissions: check /tmp ownership (likely root-only or sticky bits missing)
   command: ls -ld /tmp; stat /tmp; systemctl show docker | grep ExecStart
2. if docker uses /var/lib/docker/tmp with wrong perms: fix via systemd override
   or move build tmp: DOCKER_BUILDKIT=1 with --build-arg BUILDKIT_SYNTAX
3. for slim images specifically: also add apt-key workaround in Dockerfiles
   (use --keyring=/usr/share/keyrings/debian-archive-keyring.gpg or skip GPG check)
4. rebuild chain: freeellmapi (build + compose up) → hermes-tq → toolbox → nextcloud

data-safety checks (already done):
- freellmapi-data volume preserved
- nextcloud /mnt/HDD1/nextcloud data preserved (chown www-data done)
- toolbox / rag / homepage / traefik all verified 200

acceptance criteria:
a) docker build -t test-foo . succeeds for each service in <= 120s (no apt exit 100)
b) ./install.sh --tags containers --limit-services '["02-ai-freellmapi"]' completes with changed=0 after rebuild
c) all endpoints (freellm, cloud, rag, toolbox, homepage, traefik) 200 after full deploy

next immediate step (low-risk, can test without rebuild):
- check /tmp perms, docker daemon config, and try `DOCKER_BUILDKIT=1 docker build ...`
- only after build passes: commit Dockerfile + compose changes; run playbook

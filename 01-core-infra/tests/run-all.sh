#!/usr/bin/env bash
# tests/run-all.sh — unified validation suite for 01-core-infra.
# Runs everywhere (local Pi + GitHub Actions CI). Exit != 0 on any failure.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0
FAIL=0
FAILED_CHECKS=()

run_check() {
    local name="$1"; shift
    echo ""
    echo "▶ $name"
    if "$@" >"/tmp/check-output.log" 2>&1; then
        echo "  ✅ PASS"
        PASS=$((PASS + 1))
    else
        echo "  ❌ FAIL"
        tail -20 "/tmp/check-output.log" | sed 's/^/     /'
        FAIL=$((FAIL + 1))
        FAILED_CHECKS+=("$name")
    fi
}

echo "═══════════════════════════════════════════════════════"
echo " 01-core-infra validation suite — $(date -u +%Y-%m-%dT%H:%MZ)"
echo " root: $ROOT"
echo "═══════════════════════════════════════════════════════"

# ── 1. YAML lint ─────────────────────────────────────────────
if command -v yamllint >/dev/null; then
    run_check "yamllint: ansible YAML" \
        find ansible -type f \( -name '*.yml' -o -name '*.yaml' \) -exec yamllint -d relaxed {} +
else
    echo "⚠ yamllint not installed — skipping"
fi

# ── 2. Ansible syntax check (must run from ansible/ so ansible.cfg roles_path applies) ─
if command -v ansible-playbook >/dev/null; then
    run_check "ansible-playbook --syntax-check (site.yml)" \
        bash -c 'cd ansible && ansible-playbook -i inventories/local.yml playbooks/site.yml --syntax-check'
else
    echo "⚠ ansible-playbook not installed — skipping"
fi

# ── 3. Ansible lint (must run from ansible/ for roles_path) ───────
if command -v ansible-lint >/dev/null; then
    run_check "ansible-lint (playbooks + roles)" \
        bash -c 'cd ansible && ansible-lint --offline playbooks/site.yml'
else
    echo "⚠ ansible-lint not installed — skipping"
fi

# ── 4. Shell scripts: bash -n syntax gate on all tracked .sh ─
check_bash_syntax() {
    local bad=0
    while IFS= read -r -d '' f; do
        if ! bash -n "$f" 2>"/tmp/bashn-err.log"; then
            echo "    syntax error in: $f"
            sed 's/^/       /' "/tmp/bashn-err.log"
            bad=1
        fi
    done < <(find . -path ./node_modules -prune -o -name '*.sh' -print0 -o -name '*.bash' -print0)
    # top-level extension-less scripts
    for f in install.sh backup.sh healthcheck.sh sensors-log.sh sensors-monitor.sh sensors-daily-summary.sh; do
        [[ -f $f ]] || continue
        if ! bash -n "$f" 2>"/tmp/bashn-err.log"; then
            echo "    syntax error in: $f"
            bad=1
        fi
    done
    return $bad
}
run_check "bash -n syntax on all shell scripts" check_bash_syntax

# ── 4. Docker-compose structural validation ──────────────────
check_compose_files() {
    local bad=0 f
    while IFS= read -r -d '' f; do
        # Skip empty placeholder files (manifest-managed repo stubs)
        if ! grep -qE '^[^#[:space:]]' "$f"; then
            continue
        fi
        if command -v docker >/dev/null; then
            # Run in a temp dir copy so missing runtime .env doesn't abort validation;
            # still catches real YAML/structure errors.
            local tmpd
            tmpd=$(mktemp -d)
            cp "$f" "$tmpd/compose.yml"
            ( cd "$tmpd" && docker compose -f compose.yml config --quiet ) 2>"/tmp/compose-err.log"
            local rc=$?
            rm -rf "$tmpd"
            if (( rc )); then
                # tolerate ONLY missing env-file errors (runtime .env never committed)
                grep -q 'env file' "/tmp/compose-err.log" && grep -qv 'yaml\|syntax\|invalid' "/tmp/compose-err.log" && {
                    echo "    (skip env-dependent) $f"
                    continue
                }
                echo "    invalid compose: $f"
                sed 's/^/       /' "/tmp/compose-err.log" | grep -v 'level=warning' | head -6
                bad=1
            fi
        elif python3 -c 'import yaml' 2>/dev/null; then
            python3 - "$f" <<'PYEOF' || { echo "    invalid compose: $f"; bad=1; }
import sys, yaml
d = yaml.safe_load(open(sys.argv[1]))
assert isinstance(d, dict), "not a mapping"
svcs = d.get("services", {})
assert svcs, "no services defined"
for name, s in svcs.items():
    assert ("image" in s) or ("build" in s), f"{name}: needs image or build"
PYEOF
        fi
    done < <(find templates -name 'docker-compose*.yml' -print0 2>/dev/null; find . -maxdepth 2 -mindepth 2 \( -path './jellyfin/*' -o -path './portainer/*' -o -path './cockpit/*' -o -path './nextcloud/*' \) -name 'docker-compose*.yml' -print0 2>/dev/null)
    return $bad
}
run_check "docker compose config validation" check_compose_files

# ── 6. Docker image pinning: no :latest outside comments ─────
check_image_pinning() {
    local bad=0
    while IFS= read -r -d '' f; do
        # flag non-comment lines using :latest
        if grep -nE 'image:.*:latest' "$f" | grep -vE ':\s*#' | grep -q ':'; then
            echo "    unpinned :latest in $f:"
            grep -nE 'image:.*:latest' "$f" | grep -v '^\s*[0-9]*:\s*#' | sed 's/^/       /'
            bad=1
        fi
    done < <(find templates -name 'docker-compose*.yml' -print0 2>/dev/null; find . -maxdepth 2 -mindepth 2 \( -path './jellyfin/*' -o -path './portainer/*' -o -path './cockpit/*' -o -path './nextcloud/*' \) -name 'docker-compose*.yml' -print0 2>/dev/null)
    return $bad
}
run_check "docker images pinned (no :latest)" check_image_pinning

# ── 7. Traefik routes sanity (renders routes.yml.j2 from role vars) ──
check_routes() {
    local tpl="ansible/roles/containers/templates/routes.yml.j2"
    local defs="ansible/roles/containers/defaults/main.yml"
    [[ -f $tpl && -f $defs ]] || { echo "    routes template/vars missing"; return 1; }
    python3 - "$tpl" "$defs" <<'PYEOF'
import sys, yaml, re, jinja2
tpl_path, defs_path = sys.argv[1], sys.argv[2]
defs = yaml.safe_load(open(defs_path))
try:
    vars_ = {k: defs[k] for k in ("traefik_routes", "traefik_backends",
                                  "traefik_ip_allowlist",
                                  "traefik_tls_certresolver")}
except KeyError as e:
    raise SystemExit(f"    missing role var: {e}")
env = jinja2.Environment(trim_blocks=True, undefined=jinja2.StrictUndefined)
out = env.from_string(open(tpl_path).read()).render(**vars_)
d = yaml.safe_load(out)
routers = d.get("http", {}).get("routers", {})
services = d.get("http", {}).get("services", {})
middlewares = d.get("http", {}).get("middlewares", {})
assert routers, "no routers"
hosts = set()
for name, r in routers.items():
    assert "rule" in r and "Host(" in r["rule"], f"{name}: missing Host() rule"
    assert "service" in r, f"{name}: no service ref"
    assert r["service"] in services, \
        f"{name}: references undefined service '{r['service']}'"
    hs = re.findall(r'Host\(`([^`]+)`\)', r["rule"])
    assert hs, f"{name}: no hostname in rule"
    for h in hs:
        assert h not in hosts, f"{name}: duplicate host {h}"
        hosts.add(h)
used_svcs = {r["service"] for r in routers.values()}
used_mws = set().union(*(r.get("middlewares", []) for r in routers.values()))
orphans = set(services) - used_svcs
assert not orphans, f"backends never routed: {sorted(orphans)}"
unknown = used_mws - set(middlewares)
assert not unknown, f"undefined middlewares referenced: {sorted(unknown)}"
assert middlewares.get("ipAllowList", {}).get("ipAllowList", {})\
    .get("sourceRange"), "ipAllowList middleware missing/empty"
print(f"    validated {len(routers)} routers / {len(services)} services "
      f"(rendered from routes.yml.j2)")
PYEOF
}
run_check "traefik routes.yml router/service integrity" check_routes

# ── 7. Placeholder hygiene (templates must use macros) ───────
check_placeholders() {
    local bad=0
    # cron + systemd templates must NOT hardcode runtime paths
    while IFS= read -r -d '' f; do
        if grep -qE '/home/[a-z]+/' "$f"; then
            echo "    hardcoded /home path in: $f"
            bad=1
        fi
    done < <(find templates/cron templates/systemd -type f \( -name '*.cron' -o -name '*.service' -o -name '*.timer' \) -print0 2>/dev/null)
    return $bad
}
run_check "no hardcoded /home paths in cron/systemd templates" check_placeholders

# ── 8. Vault safety: master.key never committed ───────────────
check_vault_safety() {
    git ls-files --error-unmatch vaults/master.key >/dev/null 2>&1 && {
        echo "    vaults/master.key is TRACKED by git!"; return 1; }
    grep -q '^vaults/master.key$' .gitignore || grep -q 'master.key' .gitignore || {
        echo "    master.key not in .gitignore"; return 1; }
    return 0
}
run_check "vault master.key not tracked" check_vault_safety

# ── 9. Role structure: every role has tasks/main.yml ─────────
check_roles() {
    local bad=0 role
    for role_dir in ansible/roles/*/; do
        role=$(basename "$role_dir")
        [[ -f "$role_dir/tasks/main.yml" ]] || { echo "    role '$role' missing tasks/main.yml"; bad=1; }
    done
    return $bad
}
run_check "all roles define tasks/main.yml" check_roles

# ── 10. tools_sentries consistency ────────────────────────────
check_sentries() {
    python3 - <<'PYEOF'
import yaml
d = yaml.safe_load(open("ansible/roles/tools/defaults/main.yml"))
s = d.get("tools_sentries")
assert isinstance(s, dict) and s, "tools_sentries missing or empty"
missing_cmd = [k for k, v in s.items() if not isinstance(v, dict) or "command" not in v]
assert not missing_cmd, f"sentries without command check: {missing_cmd}"
print(f"    {len(s)} sentries ok")
PYEOF
}
run_check "tools_sentries structure valid" check_sentries

# ── summary ──────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
echo " RESULT: $PASS passed, $FAIL failed"
if (( FAIL )); then
    printf ' failed checks: %s\n' "${FAILED_CHECKS[*]}"
    echo "═══════════════════════════════════════════════════════"
    exit 1
fi
echo "═══════════════════════════════════════════════════════"

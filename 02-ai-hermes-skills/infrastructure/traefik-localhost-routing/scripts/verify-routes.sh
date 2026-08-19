#!/bin/bash
# Verify Traefik routes.yml syntax and configuration

set -euo pipefail

echo "=== Verifying Traefik routes.yml ==="

# 1. Check YAML syntax
echo "[1/4] Checking YAML syntax..."
python3 -c "import yaml, sys; yaml.safe_load(sys.stdin)" < /home/aldo/dev/04-network-traefik/routes.yml || {
    echo "❌ YAML syntax error"
    exit 1
}
echo "✅ YAML syntax OK"

# 2. Check for localhost routes
echo "[2/4] Checking localhost route configuration..."
if grep -q 'url: "http://127.0.0.1' /home/aldo/dev/04-network-traefik/routes.yml; then
    echo "✅ localhost (127.0.0.1) routes found"
else
    echo "⚠️  No localhost routes found"
fi

# 3. Check for overlapping lineinfile patterns (should NOT have these)
echo "[3/4] Checking for dangerous lineinfile patterns..."
if grep -r "lineinfile.*homepage" /home/aldo/dev/01-core-infra/ansible/roles/neo-brutalist-home/ 2>/dev/null; then
    echo "❌ DANGEROUS: lineinfile pattern for 'homepage' found in neo-brutalist-home role"
    exit 1
else
    echo "✅ No dangerous lineinfile patterns"
fi

# 4. Verify file permissions on target
echo "[4/4] Checking target file permissions..."
TARGET="/var/www/06-apps-neo-brutalist-home/routes.yml"
if [ -f "$TARGET" ]; then
    OWNER=$(stat -c '%U' "$TARGET")
    GROUP=$(stat -c '%G' "$TARGET")
    if [ "$OWNER" = "www-data" ] && [ "$GROUP" = "www-data" ]; then
        echo "✅ Target file permissions correct (www-data:www-data)"
    else
        echo "❌ Target file not owned by www-data:group (current: $OWNER:$GROUP)"
        exit 1
    fi
else
    echo "❌ Target file not found: $TARGET"
    exit 1
fi

echo ""
echo "=== All verifications passed ==="
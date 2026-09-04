#!/bin/bash

echo "=== Testing Proxy Structure Consolidation ==="
echo

echo "1. Checking folder counts..."
SERVICES_COUNT=$(ls -1 ~/dev/10-services-sablier-proxy/service-definitions/ | wc -l)
PROXIES_COUNT=$(ls -1 ~/dev/10-services-sablier-proxy/simple-proxies/ | wc -l)
echo "   service-definitions/: $SERVICES_COUNT folders"
echo "   simple-proxies/: $PROXIES_COUNT folders"

echo ""
echo "2. Validating Traefik configuration consistency..."
BACKENDS_SERVICES=$(grep -A 30 "traefik_backends:" ~/dev/01-core-infra/ansible/roles/containers/defaults/main.yml | grep "^  [a-z]" | cut -d: -f1 | sort)
ROUTES_SERVICES=$(grep -A 30 "traefik_routes:" ~/dev/01-core-infra/ansible/roles/containers/defaults/main.yml | grep "service:" | cut -d: -f2 | tr -d ' ' | sort)

echo "   Services in traefik_backends:"
echo "   $(echo "$BACKENDS_SERVICES" | sed '/^$/d' | paste -sd ', ' -)"
echo "   Services in traefik_routes:"
echo "   $(echo "$ROUTES_SERVICES" | sed '/^$/d' | paste -sd ', ' -)"

MISSING_IN_ROUTES=$(comm -23 <(echo "$BACKENDS_SERVICES") <(echo "$ROUTES_SERVICES"))
MISSING_IN_BACKENDS=$(comm -13 <(echo "$BACKENDS_SERVICES") <(echo "$ROUTES_SERVICES"))

if [ -n "$MISSING_IN_ROUTES" ]; then
    echo "   ❌ Services in backends but NOT in routes: $MISSING_IN_ROUTES"
else
    echo "   ✓ All backend services are in routes"
fi

if [ -n "$MISSING_IN_BACKENDS" ]; then
    echo "   ❌ Services in routes but NOT in backends: $MISSING_IN_BACKENDS"
else
    echo "   ✓ All route services are in backends"
fi

echo ""
echo "3. Validating docker-compose.yml files..."
VALID_PROXIES=0
INVALID_PROXIES=0

for proxy in ~/dev/10-services-sablier-proxy/simple-proxies/*-proxy/; do
    if [ -f "${proxy}docker-compose.yml" ]; then
        if docker compose -f "${proxy}docker-compose.yml" config >/dev/null 2>&1; then
            echo "   ✓ $(basename "$proxy")"
            ((VALID_PROXIES++))
        else
            echo "   ❌ $(basename "$proxy")"
            ((INVALID_PROXIES++))
        fi
    else
        echo "   ⚠ $(basename "$proxy") - missing docker-compose.yml"
        ((INVALID_PROXIES++))
    fi
done

echo "   Valid proxy configs: $VALID_PROXIES"
echo "   Invalid/missing: $INVALID_PROXIES"

echo ""
echo "4. Checking root ~/dev/ for stray proxy folders..."
ROOT_PROXIES=$(ls -1 ~/dev/*-proxy 2>/dev/null | grep -v "10-services-sablier-proxy" | wc -l)
if [ "$ROOT_PROXIES" -eq 0 ]; then
    echo "   ✓ No proxy folders at ~/dev/ root"
else
    echo "   ❌ Found $ROOT_PROXIES proxy folders at ~/dev/ root"
fi

echo ""
echo "=== Summary ==="
echo "✅ Service definition folder count: $SERVICES_COUNT (expected: 16)"
echo "✅ Proxy config folder count: $PROXIES_COUNT (expected: 16)"
echo "✅ All docker-compose.yml files validated: $VALID_PROXIES"

if [ "$SERVICES_COUNT" -eq 16 ] && [ "$PROXIES_COUNT" -eq 16 ] && [ "$VALID_PROXIES" -eq 16 ] && [ "$ROOT_PROXIES" -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi

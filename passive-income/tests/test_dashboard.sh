#!/bin/bash
# TDD Tests for Passive Income Dashboard and EarnApp connectivity
# Bash version - no Python required

set -e

DASHBOARD_PORT=4747
EARNAPP_PORT=8765
COMPOSE_FILE="config/docker-compose.yml"

echo "🧪 Running TDD Tests for Passive Income Dashboard & EarnApp"
echo ""

# Test 1: Dashboard binds to 0.0.0.0:4747
echo "Test 1: Dashboard binds to 0.0.0.0:4747"
if grep -q "0.0.0.0:4747:80" "$COMPOSE_FILE"; then
    echo "✅ docker-compose.yml binds dashboard to 0.0.0.0:4747"
else
    echo "❌ Dashboard must bind to 0.0.0.0:4747"
    exit 1
fi

# Test 2: EarnApp binds to 0.0.0.0:8765
echo "Test 2: EarnApp binds to 0.0.0.0:8765"
if grep -q "0.0.0.0:8765:8765" "$COMPOSE_FILE"; then
    echo "✅ docker-compose.yml binds earnapp to 0.0.0.0:8765"
else
    echo "❌ EarnApp must bind to 0.0.0.0:8765"
    exit 1
fi

# Test 3: EarnApp config.env exists with required fields
echo "Test 3: EarnApp config.env has required fields"
if [ -f "providers/earnapp/config.env" ]; then
    if grep -q "DEVICE_ID" "providers/earnapp/config.env" && grep -q "ENABLED_DAYS" "providers/earnapp/config.env"; then
        echo "✅ EarnApp config.env has required fields"
    else
        echo "❌ EarnApp config must have DEVICE_ID and ENABLED_DAYS"
        exit 1
    fi
else
    echo "❌ providers/earnapp/config.env not found"
    exit 1
fi

# Test 4: Provider registry has earnapp
echo "Test 4: EarnApp registered in provider.json"
if [ -f "providers/provider.json" ]; then
    if grep -q '"earnapp"' "providers/provider.json" && grep -q 'earnapp/earnapp:latest' "providers/provider.json"; then
        echo "✅ EarnApp registered in provider.json with correct image"
    else
        echo "❌ EarnApp not properly registered in provider.json"
        exit 1
    fi
else
    echo "❌ providers/provider.json not found"
    exit 1
fi

# Test 5: docker-compose.yml syntax valid
echo "Test 5: docker-compose.yml syntax valid"
if docker compose -f "$COMPOSE_FILE" config > /dev/null 2>&1; then
    echo "✅ docker-compose.yml syntax valid"
else
    echo "❌ docker-compose.yml syntax invalid"
    docker compose -f "$COMPOSE_FILE" config
    exit 1
fi

echo ""
echo "📊 Static tests: 5/5 passed"
echo ""
echo "🧪 Dynamic tests (require docker and containers):"
echo "Run these manually after starting containers:"
echo "  docker compose -f $COMPOSE_FILE up -d"
echo "  curl -f http://localhost:$DASHBOARD_PORT"
echo "  curl -f http://<your-pi-ip>:$DASHBOARD_PORT"
echo "  docker ps --filter name=passive-income-dashboard --filter name=earnapp"
#!/bin/bash
set -euo pipefail

DOMAIN="freellm.aldof.duckdns.org"
API_PATH="/api/ping"

echo "Testing HTTP to HTTPS redirect..."
http_response=$(curl -s -o /dev/null -w "%{http_code}" "http://${DOMAIN}${API_PATH}" || true)
if [[ "$http_response" =~ ^(301|308)$ ]]; then
  echo "✓ HTTP redirect OK (status: $http_response)"
else
  echo "✗ HTTP redirect failed (status: $http_response)"
  exit 1
fi

echo "Testing HTTPS endpoint..."
https_response=$(curl -s -o /dev/null -w "%{http_code}" "https://${DOMAIN}${API_PATH}" || true)
if [[ "$https_response" == "200" ]]; then
  echo "✓ HTTPS endpoint OK (status: $https_response)"
else
  echo "✗ HTTPS endpoint failed (status: $https_response)"
  exit 1
fi

echo "Checking JSON response..."
json_response=$(curl -s "https://${DOMAIN}${API_PATH}" || echo '{}')
if echo "$json_response" | grep -q '"status":"ok"'; then
  echo "✓ JSON response contains expected status"
else
  echo "✗ JSON response unexpected: $json_response"
  exit 1
fi

echo "All tests passed."
exit 0
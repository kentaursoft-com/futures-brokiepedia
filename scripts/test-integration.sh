#!/bin/bash
# Integration test for Futures Brokiepedia

set -e

API_URL=${API_URL:-"http://localhost:8080"}
WORKER_URL=${WORKER_URL:-""}

echo "🧪 Futures Brokiepedia Integration Tests"
echo "========================================"
echo "API URL: $API_URL"
echo ""

# Test 1: Health endpoint
echo "Test 1: Health Check"
response=$(curl -s "$API_URL/health" || echo "{}")
if echo "$response" | grep -q "ok"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "Response: $response"
fi

# Test 2: State endpoint
echo ""
echo "Test 2: State Endpoint"
response=$(curl -s "$API_URL/api/v1/state" || echo "{}")
if echo "$response" | grep -q "system_status"; then
    echo "✅ State endpoint working"
else
    echo "❌ State endpoint failed"
fi

# Test 3: Departments endpoint
echo ""
echo "Test 3: Departments Endpoint"
response=$(curl -s "$API_URL/api/v1/departments" || echo "{}")
if echo "$response" | grep -q "departments"; then
    echo "✅ Departments endpoint working"
else
    echo "❌ Departments endpoint failed"
fi

# Test 4: Positions endpoint
echo ""
echo "Test 4: Positions Endpoint"
response=$(curl -s "$API_URL/api/v1/positions" || echo "{}")
if echo "$response" | grep -q "positions"; then
    echo "✅ Positions endpoint working"
else
    echo "❌ Positions endpoint failed"
fi

# Test Worker if URL provided
if [ -n "$WORKER_URL" ]; then
    echo ""
    echo "Test 5: Worker Health"
    response=$(curl -s "$WORKER_URL/health" || echo "{}")
    if echo "$response" | grep -q "ok"; then
        echo "✅ Worker health check passed"
    else
        echo "❌ Worker health check failed"
    fi
fi

echo ""
echo "========================================"
echo "Integration tests complete!"

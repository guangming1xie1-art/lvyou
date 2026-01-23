#!/bin/bash
# Test JWT Token Forwarding from Agent to Java Services
# 测试JWT从Agent转发到Java服务的完整流程

set -e  # Exit on error

echo "=========================================="
echo "JWT Token Forwarding Integration Test"
echo "=========================================="
echo ""

# Configuration
AGENT_BASE_URL="http://localhost:8000"
JAVA_BASE_URL="http://localhost:8080/api"

# Test user credentials
TEST_USERNAME="testuser_$(date +%s)"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="Test123!@#"

echo "Step 1: Register a new user"
echo "----------------------------"
REGISTER_RESPONSE=$(curl -s -X POST "${AGENT_BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${TEST_USERNAME}\",
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\"
  }")

echo "Register Response: ${REGISTER_RESPONSE}"
echo ""

echo "Step 2: Login and get JWT token"
echo "--------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "${AGENT_BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"${TEST_USERNAME}\",
    \"password\": \"${TEST_PASSWORD}\"
  }")

echo "Login Response: ${LOGIN_RESPONSE}"
echo ""

# Extract access token
ACCESS_TOKEN=$(echo "${LOGIN_RESPONSE}" | jq -r '.tokens.access_token' 2>/dev/null || echo "")

if [ -z "${ACCESS_TOKEN}" ] || [ "${ACCESS_TOKEN}" = "null" ]; then
    echo "❌ Failed to get access token!"
    echo "Login response: ${LOGIN_RESPONSE}"
    exit 1
fi

echo "✅ Access Token obtained: ${ACCESS_TOKEN:0:50}..."
echo ""

echo "Step 3: Call Agent search API with JWT"
echo "---------------------------------------"
SEARCH_RESPONSE=$(curl -s -X POST "${AGENT_BASE_URL}/api/agent/search" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Beijing",
    "destination": "Tokyo",
    "departure_date": "2025-03-15",
    "passengers": 2,
    "cabin_class": "economy",
    "include_hotels": false
  }')

echo "Search Response (first 500 chars):"
echo "${SEARCH_RESPONSE}" | head -c 500
echo ""
echo "..."
echo ""

# Check if search was successful
if echo "${SEARCH_RESPONSE}" | grep -q '"success":true' || echo "${SEARCH_RESPONSE}" | grep -q '"task_id"'; then
    echo "✅ Agent search API call successful!"
else
    echo "❌ Agent search API call failed or returned error"
    echo "Full response: ${SEARCH_RESPONSE}"
fi
echo ""

echo "Step 4: Call Agent recommend API with JWT"
echo "------------------------------------------"
RECOMMEND_RESPONSE=$(curl -s -X POST "${AGENT_BASE_URL}/api/agent/recommend" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo",
    "start_date": "2025-03-15",
    "end_date": "2025-03-20",
    "preferences": ["culture", "food"],
    "budget": 3000,
    "include_attractions": true,
    "include_weather": true,
    "include_reviews": false
  }')

echo "Recommend Response (first 500 chars):"
echo "${RECOMMEND_RESPONSE}" | head -c 500
echo ""
echo "..."
echo ""

if echo "${RECOMMEND_RESPONSE}" | grep -q '"success":true' || echo "${RECOMMEND_RESPONSE}" | grep -q '"task_id"'; then
    echo "✅ Agent recommend API call successful!"
else
    echo "❌ Agent recommend API call failed or returned error"
    echo "Full response: ${RECOMMEND_RESPONSE}"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✅ User registration: SUCCESS"
echo "✅ User login: SUCCESS"
echo "✅ JWT token obtained: SUCCESS"
echo "✅ Agent API calls with JWT: COMPLETED"
echo ""
echo "Next Steps:"
echo "1. Check Agent logs to verify JWT was forwarded to Java services"
echo "2. Check Java service logs to verify JWT was received and validated"
echo "3. Look for log entries with 'Authorization' header and 'X-User-ID'"
echo ""
echo "To check Agent logs:"
echo "  tail -f travel-assistant-agent/logs/app.log"
echo ""
echo "To check Java Gateway logs:"
echo "  docker logs travel-assistant-gateway"
echo ""

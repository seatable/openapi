#!/usr/bin/env bash
#
# Waits for SeaTable to be ready and creates a test user via admin API.

set -euo pipefail

SEATABLE_URL="${SEATABLE_URL:-http://localhost}"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin1234"
TEST_USER_EMAIL="testuser@example.com"
TEST_USER_PASSWORD="testuser1234"

TIMEOUT=40
INTERVAL=10

echo "Waiting for SeaTable to become available..."
start_time=$(date +%s)

while true; do
    if curl -sf "${SEATABLE_URL}/dtable-server/ping/" > /dev/null 2>&1; then
        echo "SeaTable is ready."
        break
    fi

    elapsed=$(( $(date +%s) - start_time ))
    if [ "$elapsed" -ge "$TIMEOUT" ]; then
        echo "Timeout: SeaTable did not become available within ${TIMEOUT}s."
        exit 1
    fi

    echo "  Not ready yet (${elapsed}s elapsed). Retrying in ${INTERVAL}s..."
    sleep "$INTERVAL"
done

# Wait for dtable-web (API) to be ready
echo "Waiting for SeaTable API to become available..."
start_time=$(date +%s)

while true; do
    if curl -sf "${SEATABLE_URL}/api2/ping/" > /dev/null 2>&1; then
        echo "SeaTable API is ready."
        break
    fi

    elapsed=$(( $(date +%s) - start_time ))
    if [ "$elapsed" -ge "$TIMEOUT" ]; then
        echo "Timeout: SeaTable API did not become available within ${TIMEOUT}s."
        exit 1
    fi

    echo "  API not ready yet (${elapsed}s elapsed). Retrying in ${INTERVAL}s..."
    sleep "$INTERVAL"
done

# Get admin account token
echo "Obtaining admin token..."
start_time=$(date +%s)

while true; do
    AUTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SEATABLE_URL}/api2/auth-token/" \
        --data-urlencode "username=${ADMIN_EMAIL}" \
        --data-urlencode "password=${ADMIN_PASSWORD}")
    AUTH_BODY=$(echo "$AUTH_RESPONSE" | sed '$d')
    AUTH_STATUS=$(echo "$AUTH_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')

    if [ "$AUTH_STATUS" = "200" ]; then
        echo "Admin token obtained."
        break
    fi

    elapsed=$(( $(date +%s) - start_time ))
    if [ "$elapsed" -ge "$TIMEOUT" ]; then
        echo "Timeout: Auth-token request failed after ${TIMEOUT}s (HTTP ${AUTH_STATUS})."
        exit 1
    fi

    echo "  Auth not ready yet (HTTP ${AUTH_STATUS}, ${elapsed}s elapsed). Retrying in ${INTERVAL}s..."
    sleep "$INTERVAL"
done

ADMIN_TOKEN=$(echo "$AUTH_BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

# Create test user
echo "Creating test user..."
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${SEATABLE_URL}/api/v2.1/admin/users/" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"${TEST_USER_EMAIL}\", \"password\": \"${TEST_USER_PASSWORD}\", \"name\": \"Test User\", \"is_staff\": false, \"is_active\": true}")

if [ "$response" -eq 200 ] || [ "$response" -eq 201 ]; then
    echo "Test user created."
elif [ "$response" -eq 400 ]; then
    echo "Test user already exists (HTTP 400). Continuing."
else
    echo "Failed to create test user (HTTP ${response})."
    exit 1
fi

echo "Setup complete."

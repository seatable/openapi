#!/usr/bin/env bash
#
# Waits for SeaTable to be ready and creates a test user via admin API.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load credentials from .env
set -a
source "${SCRIPT_DIR}/.env"
set +a

TIMEOUT=60
INTERVAL=10

echo "Waiting for SeaTable to become available..."
start_time=$(date +%s)

while true; do
    if curl -sf "${SEATABLE_SERVER}/dtable-server/ping/" > /dev/null 2>&1; then
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
    if curl -sf "${SEATABLE_SERVER}/api2/ping/" > /dev/null 2>&1; then
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
    AUTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${SEATABLE_SERVER}/api2/auth-token/" \
        --data-urlencode "username=${SEATABLE_ADMIN_USERNAME}" \
        --data-urlencode "password=${SEATABLE_ADMIN_PASSWORD}")
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
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${SEATABLE_SERVER}/api/v2.1/admin/users/" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"${SEATABLE_USERNAME}\", \"password\": \"${SEATABLE_PASSWORD}\", \"name\": \"Test User\", \"is_staff\": false, \"is_active\": true}")

if [ "$response" -eq 200 ] || [ "$response" -eq 201 ]; then
    echo "Test user created."
elif [ "$response" -eq 400 ]; then
    echo "Test user already exists (HTTP 400). Continuing."
else
    echo "Failed to create test user (HTTP ${response})."
    exit 1
fi

SETTINGS_FILE="/shared/seatable/conf/dtable_web_settings.py"

echo "Configuring dtable-web..."
docker exec -i seatable-server bash -c "cat >> ${SETTINGS_FILE}" <<'SETTINGS'

CLOUD_MODE = True
MULTI_TENANCY = True
ORG_MEMBER_QUOTA_ENABLED = True
ORG_MEMBER_QUOTA_DEFAULT = 25

ENABLED_ROLE_PERMISSIONS = {
    'default': {
        'can_add_dtable': True,
        'can_add_group': True,
        'can_generate_share_link': True,
        'can_create_common_dataset': True,
        'can_generate_external_link': True,
        'role_asset_quota': '1G',
        'row_limit': 2000,
        'can_use_advanced_permissions': False,
        'can_run_python_script': False,
        'snapshot_days': 30,
        'can_archive_rows': False,
        'can_schedule_run_script': True
    },
    'org_default': {
        'can_add_dtable': True,
        'can_add_group': True,
        'can_generate_share_link': True,
        'can_create_common_dataset': True,
        'can_generate_external_link': True,
        'role_asset_quota': '2G',
        'row_limit': 10000,
        'snapshot_days': 30,
        'can_use_advanced_permissions': False,
        'can_use_advanced_customization': False,
        'can_use_automation_rules': False,
        'can_run_python_script': True,
        'scripts_running_limit': 100,
        'can_archive_rows': False,
        'can_schedule_run_script': True,
        'monthly_api_call_limit_per_user': 120,
        # 6.0
        'ai_credit_per_user': 0,
        'can_use_saml': False,
    },
    'org_plus': {
        'can_add_dtable': True,
        'can_add_group': True,
        'can_generate_share_link': True,
        'can_create_common_dataset': True,
        'can_generate_external_link': True,
        'role_asset_quota': '50G',
        'row_limit': 50000,
        'snapshot_days': 180,
        'can_use_advanced_permissions': True,
        'can_use_advanced_customization': False,
        'can_use_automation_rules': False,
        'can_run_python_script': True,
        'scripts_running_limit': 5000,
        'can_archive_rows': False,
        'can_schedule_run_script': True,
        'monthly_api_call_limit_per_user': 10000,
        # 6.0
        'ai_credit_per_user': 0,
        'can_use_saml': False,
    },
    'org_enterprise': {
        'can_add_dtable': True,
        'can_add_group': True,
        'can_generate_share_link': True,
        'can_create_common_dataset': True,
        'can_generate_external_link': True,
        'role_asset_quota': '100G',
        'row_limit': -1,
        'snapshot_days': 365,
        'can_use_advanced_permissions': True,
        'can_use_advanced_customization': True,
        'can_use_automation_rules': True,
        'can_run_python_script': True,
        'scripts_running_limit': -1,
        'can_archive_rows': True,
        'can_schedule_run_script': True,
        'monthly_api_call_limit_per_user': 50000,
        # 6.0
        'ai_credit_per_user': 500,
        'can_use_saml': True,
    },
}

REST_FRAMEWORK_THROTTLING_WHITELIST = ['172.16.0.0/12', '192.168.0.0/16', '127.0.0.1']
SETTINGS

echo "Restarting SeaTable to apply settings..."
docker exec seatable-server /templates/seatable.sh restart

echo "Setup complete."

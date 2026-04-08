"""Tests to validate documentation accuracy against the live API.

These tests verify that status codes, response schemas, and endpoint behavior
match what is documented in the OpenAPI specs.
"""
import pytest
import requests
from conftest import (
    BASE_URL, Secret, Base,
    authentication_schema, user_account_operations,
)
from schemathesis import Case


# ---------------------------------------------------------------------------
# 1. Authentication: 401 for invalid Account-Token
#    Verified: API returns 401 with {"detail": "Invalid token"}
# ---------------------------------------------------------------------------

def test_account_token_invalid_returns_401(account_token: Secret):
    """getBaseTokenWithAccountToken returns 401 for an invalid Account-Token."""
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithAccountToken') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test'})
    response = case.call(headers={'Authorization': 'Bearer invalid-token-12345'})

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid token'


def test_account_token_missing_returns_403():
    """getBaseTokenWithAccountToken returns 403 when no token is provided."""
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithAccountToken') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test'})
    response = case.call(headers={})

    assert response.status_code == 403


def test_account_token_base_not_found(account_token: Secret):
    """getBaseTokenWithAccountToken returns 404 for a non-existent base."""
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithAccountToken') \
        .Case(path_parameters={'workspace_id': 99999, 'base_name': 'Nonexistent'})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 2. Authentication: error responses for API-Token CRUD endpoints
#    Verified against SeaTable 6.1.8: consistent 401/403/404 pattern
# ---------------------------------------------------------------------------

def test_listApiTokens_invalid_token():
    """listApiTokens returns 401 for an invalid Account-Token."""
    case: Case = authentication_schema.find_operation_by_id('listApiTokens') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test'})
    response = case.call(headers={'Authorization': 'Bearer invalid-token-12345'})

    assert response.status_code == 401


def test_listApiTokens_no_token():
    """listApiTokens returns 403 when no token is provided."""
    case: Case = authentication_schema.find_operation_by_id('listApiTokens') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test'})
    response = case.call(headers={})

    assert response.status_code == 403


def test_listApiTokens_not_found(account_token: Secret):
    """listApiTokens returns 404 for a non-existent workspace."""
    case: Case = authentication_schema.find_operation_by_id('listApiTokens') \
        .Case(path_parameters={'workspace_id': 99999, 'base_name': 'Nonexistent'})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 404


def test_createApiToken_invalid_token():
    """createApiToken returns 401 for an invalid Account-Token."""
    case: Case = authentication_schema.find_operation_by_id('createApiToken') \
        .Case(
            path_parameters={'workspace_id': 1, 'base_name': 'Test'},
            body={'app_name': 'test', 'permission': 'rw'},
        )
    response = case.call(headers={'Authorization': 'Bearer invalid-token-12345'})

    assert response.status_code == 401


def test_createApiToken_no_token():
    """createApiToken returns 403 when no token is provided."""
    case: Case = authentication_schema.find_operation_by_id('createApiToken') \
        .Case(
            path_parameters={'workspace_id': 1, 'base_name': 'Test'},
            body={'app_name': 'test', 'permission': 'rw'},
        )
    response = case.call(headers={})

    assert response.status_code == 403


def test_createApiToken_missing_app_name(account_token: Secret):
    """createApiToken returns 400 when the required app_name is missing."""
    case: Case = authentication_schema.find_operation_by_id('createApiToken') \
        .Case(
            path_parameters={'workspace_id': 99999, 'base_name': 'Nonexistent'},
            body={'permission': 'rw'},
        )
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 400


def test_createTempApiToken_invalid_token():
    """createTempApiToken returns 401 for an invalid Account-Token."""
    case: Case = authentication_schema.find_operation_by_id('createTempApiToken') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test'})
    response = case.call(headers={'Authorization': 'Bearer invalid-token-12345'})

    assert response.status_code == 401


def test_createTempApiToken_no_token():
    """createTempApiToken returns 403 when no token is provided."""
    case: Case = authentication_schema.find_operation_by_id('createTempApiToken') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test'})
    response = case.call(headers={})

    assert response.status_code == 403


def test_createTempApiToken_not_found(account_token: Secret):
    """createTempApiToken returns 404 for a non-existent workspace."""
    case: Case = authentication_schema.find_operation_by_id('createTempApiToken') \
        .Case(path_parameters={'workspace_id': 99999, 'base_name': 'Nonexistent'})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 404


def test_updateApiToken_no_token():
    """updateApiToken returns 403 when no token is provided."""
    case: Case = authentication_schema.find_operation_by_id('updateApiToken') \
        .Case(
            path_parameters={'workspace_id': 1, 'base_name': 'Test', 'app_name': 'Nonexistent'},
            body={'permission': 'rw'},
        )
    response = case.call(headers={})

    assert response.status_code == 403


def test_updateApiToken_not_found(account_token: Secret):
    """updateApiToken returns 404 for a non-existent base."""
    case: Case = authentication_schema.find_operation_by_id('updateApiToken') \
        .Case(
            path_parameters={'workspace_id': 1, 'base_name': 'Test', 'app_name': 'Nonexistent'},
            body={'permission': 'rw'},
        )
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 404


def test_deleteApiToken_no_token():
    """deleteApiToken returns 403 when no token is provided."""
    case: Case = authentication_schema.find_operation_by_id('deleteApiToken') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test', 'app_name': 'Nonexistent'})
    response = case.call(headers={})

    assert response.status_code == 403


def test_deleteApiToken_not_found(account_token: Secret):
    """deleteApiToken returns 404 for a non-existent base."""
    case: Case = authentication_schema.find_operation_by_id('deleteApiToken') \
        .Case(path_parameters={'workspace_id': 1, 'base_name': 'Test', 'app_name': 'Nonexistent'})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 3. Authentication: error responses for Base-Token endpoints
#    Verified: getBaseTokenWithApiToken returns 403 (not 401) for invalid tokens
# ---------------------------------------------------------------------------

def test_getBaseTokenWithApiToken_invalid_token():
    """getBaseTokenWithApiToken returns 403 for an invalid API-Token."""
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithApiToken').Case()
    response = case.call(headers={'Authorization': 'Token invalid-api-token-xyz'})

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 4. Authentication: login error responses
#    Verified: 400 with non_field_errors for wrong credentials
# ---------------------------------------------------------------------------

def test_getAccountTokenfromUsername_wrong_password():
    """getAccountTokenfromUsername returns 400 for wrong credentials."""
    case: Case = authentication_schema.find_operation_by_id('getAccountTokenfromUsername') \
        .Case(body={'username': 'nobody@example.com', 'password': 'wrong'})
    response = case.call()

    assert response.status_code == 400
    assert 'non_field_errors' in response.json()


# ---------------------------------------------------------------------------
# 5. Python scheduler: month parameter format is YYYYMM (no hyphen)
#    Source: dtable-web AdminRunScriptStatisticsView uses strptime('%Y%m')
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="Python scheduler feature may not be enabled on test server (HTTP 406)")
def test_python_scheduler_month_format(system_admin_account_token: Secret):
    """Verify that the month parameter accepts YYYYMM format (without hyphen)."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # YYYYMM format (correct per source code)
    response = requests.get(
        f'{BASE_URL}/api/v2.1/admin/statistics/scripts-running/',
        headers=headers,
        params={'month': '202603'},
    )

    assert response.status_code == 200


@pytest.mark.xfail(reason="Python scheduler feature may not be enabled on test server (HTTP 406)")
def test_python_scheduler_month_hyphen_rejected(system_admin_account_token: Secret):
    """Verify that YYYY-MM format (with hyphen) is rejected by the API."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # YYYY-MM format (wrong per source code)
    response = requests.get(
        f'{BASE_URL}/api/v2.1/admin/statistics/scripts-running/',
        headers=headers,
        params={'month': '2026-03'},
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="Python scheduler feature may not be enabled on test server (HTTP 406)")
def test_python_scheduler_without_month_defaults_to_current(system_admin_account_token: Secret):
    """Verify that omitting the month parameter defaults to the current month."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    response = requests.get(
        f'{BASE_URL}/api/v2.1/admin/statistics/scripts-running/',
        headers=headers,
    )

    assert response.status_code == 200

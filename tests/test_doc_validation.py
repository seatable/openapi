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


# ---------------------------------------------------------------------------
# 2. Python scheduler: month parameter format is YYYYMM (no hyphen)
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

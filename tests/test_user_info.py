import pytest
from conftest import Base, Secret, user_account_operations, system_admin_account_operations, USERNAME, ADMIN_USERNAME
from schemathesis import Case


def test_getPublicUserInfo(account_token: Secret, system_admin_account_token: Secret):
    """Look up public info for the admin user."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # First get the admin's internal user_id
    case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    admin = next(u for u in response.json()['data'] if u['contact_email'] == ADMIN_USERNAME)
    admin_user_id = admin['email']

    # Now look up public info with regular user token
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = user_account_operations.find_operation_by_id('getPublicUserInfo') \
        .Case(path_parameters={'user_id': admin_user_id})
    response = case.call(headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert 'name' in data
    assert 'avatar_url' in data


def test_listPublicUserInfos(account_token: Secret, system_admin_account_token: Secret):
    """Look up public info for multiple users."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # Get internal user_ids
    case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    user_ids = [u['email'] for u in response.json()['data']]

    # Look up public info
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = user_account_operations.find_operation_by_id('listPublicUserInfos') \
        .Case(body={'user_id_list': user_ids})
    response = case.call(headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert 'user_list' in data
    assert len(data['user_list']) >= 2

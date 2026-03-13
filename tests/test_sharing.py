from conftest import (
    Base, Secret,
    authentication_schema, user_account_operations,
)
from schemathesis import Case


def test_share_lifecycle(base: Base, account_token: Secret, system_admin_account_token: Secret):
    """Tests createUserShare, listMyShares, updateUserShare, deleteUserShare in sequence."""
    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}
    headers = {'Authorization': f'Bearer {account_token.value}'}
    admin_headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # We need the admin's internal user ID (xxx@auth.local format)
    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers=admin_headers)
    assert response.status_code == 200
    admin_email = response.json()['email']

    # 1. Create share (share base with admin user, read-only)
    body = {'email': admin_email, 'permission': 'r'}
    case: Case = user_account_operations.find_operation_by_id('createUserShare') \
        .Case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 201

    # 2. List shares (as admin, verify the share appears)
    case: Case = user_account_operations.find_operation_by_id('listMyShares').Case()
    response = case.call(headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert 'table_list' in data
    shared_names = [t['name'] for t in data['table_list']]
    assert 'Automated Tests' in shared_names

    shared_base = next(t for t in data['table_list'] if t['name'] == 'Automated Tests')
    assert shared_base['permission'] == 'r'

    # 3. Update share (change to read-write)
    body = {'email': admin_email, 'permission': 'rw'}
    case: Case = user_account_operations.find_operation_by_id('updateUserShare') \
        .Case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] is True

    # 4. Delete share
    body = {'email': admin_email}
    case: Case = user_account_operations.find_operation_by_id('deleteUserShare') \
        .Case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] is True

    # Verify share is gone
    case: Case = user_account_operations.find_operation_by_id('listMyShares').Case()
    response = case.call(headers=admin_headers)

    assert response.status_code == 200
    shared_names = [t['name'] for t in response.json()['table_list']]
    assert 'Automated Tests' not in shared_names

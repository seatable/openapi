from conftest import (
    Secret, system_admin_account_operations, USERNAME, ADMIN_USERNAME,
    create_group, delete_group,
)
from schemathesis import Case


def test_listGroups(system_admin_account_token: Secret, account_token: Secret):
    """List groups as admin, verify a known group appears."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # Create a group as regular user so we have something to find
    group_id, _ = create_group(account_token, 'admin-list-test')

    try:
        case: Case = system_admin_account_operations.find_operation_by_id('listGroups') \
            .Case(query={'page': 1, 'per_page': 25})
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert 'groups' in data
        assert isinstance(data['groups'], list)

        group_ids = [g['id'] for g in data['groups']]
        assert group_id in group_ids

        group = next(g for g in data['groups'] if g['id'] == group_id)
        assert group['name'] == 'admin-list-test'

    finally:
        delete_group(account_token, group_id)


def test_listGroups_search(system_admin_account_token: Secret, account_token: Secret):
    """Search groups by name."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    group_id, _ = create_group(account_token, 'unique-search-group')

    try:
        case: Case = system_admin_account_operations.find_operation_by_id('listGroups') \
            .Case(query={'name': 'unique-search'})
        response = case.call(headers=headers)

        assert response.status_code == 200
        groups = response.json()['groups']
        assert any(g['id'] == group_id for g in groups)

    finally:
        delete_group(account_token, group_id)


def test_transferGroup(system_admin_account_token: Secret, account_token: Secret):
    """Transfer group ownership from testuser to admin."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    group_id, _ = create_group(account_token, 'transfer-test-group')

    try:
        # Find admin's internal user_id
        case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
        response = case.call(headers=headers)
        admin_user = next(u for u in response.json()['data'] if u['contact_email'] == ADMIN_USERNAME)
        admin_user_id = admin_user['email']

        # Transfer group to admin
        path_parameters = {'group_id': group_id}
        body = {'new_owner': admin_user_id}
        case: Case = system_admin_account_operations.find_operation_by_id('transferGroup') \
            .Case(path_parameters=path_parameters, body=body)
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert data['id'] == group_id
        assert data['owner'] == admin_user_id

    finally:
        # Delete as admin (now the owner)
        path_parameters = {'group_id': group_id}
        case: Case = system_admin_account_operations.find_operation_by_id('deleteGroup') \
            .Case(path_parameters=path_parameters)
        case.call(headers=headers)

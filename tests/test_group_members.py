import pytest
from conftest import (
    Base, Secret, user_account_operations, system_admin_account_operations,
    USERNAME, ADMIN_USERNAME, create_group, delete_group,
)
from schemathesis import Case


def _get_internal_user_id(system_admin_account_token: Secret, contact_email: str) -> str:
    """Look up internal user_id (xxx@auth.local) by contact email."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    user = next(u for u in response.json()['data'] if u['contact_email'] == contact_email)
    return user['email']


def test_group_member_lifecycle(account_token: Secret, system_admin_account_token: Secret):
    """Tests addGroupMember, getGroupMembers, updateGroupRole, removeGroupMember."""
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # Create a group owned by the test user
    group_id, workspace_id = create_group(account_token, 'test-group-members')

    try:
        admin_user_id = _get_internal_user_id(system_admin_account_token, ADMIN_USERNAME)

        # 1. Add admin as group member
        case: Case = user_account_operations.find_operation_by_id('addGroupMember') \
            .Case(
                path_parameters={'group_id': group_id},
                body={'email': admin_user_id},
            )
        response = case.call(headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data['contact_email'] == ADMIN_USERNAME

        # 2. List group members
        case: Case = user_account_operations.find_operation_by_id('getGroupMembers') \
            .Case(path_parameters={'group_id': group_id})
        response = case.call(headers=headers)

        assert response.status_code == 200
        members = response.json()
        assert len(members) >= 2  # owner + added member

        # 3. Remove group member
        case: Case = user_account_operations.find_operation_by_id('removeGroupMember') \
            .Case(
                path_parameters={'group_id': group_id, 'group_member': admin_user_id},
            )
        response = case.call(headers=headers)

        assert response.status_code == 200

    finally:
        delete_group(account_token, group_id)


def test_updateGroupRole(account_token: Secret, system_admin_account_token: Secret):
    headers = {'Authorization': f'Bearer {account_token.value}'}
    group_id, workspace_id = create_group(account_token, 'test-update-role')

    try:
        admin_user_id = _get_internal_user_id(system_admin_account_token, ADMIN_USERNAME)

        # Add member first
        case: Case = user_account_operations.find_operation_by_id('addGroupMember') \
            .Case(
                path_parameters={'group_id': group_id},
                body={'email': admin_user_id},
            )
        case.call(headers=headers)

        # Update role
        case: Case = user_account_operations.find_operation_by_id('updateGroupRole') \
            .Case(
                path_parameters={'group_id': group_id, 'group_member': admin_user_id},
                body={'is_admin': True},
            )
        response = case.call(headers=headers)

        assert response.status_code == 200

    finally:
        delete_group(account_token, group_id)


def test_searchGroup(account_token: Secret):
    headers = {'Authorization': f'Bearer {account_token.value}'}

    group_id, workspace_id = create_group(account_token, 'test-search-group-unique')

    try:
        case: Case = user_account_operations.find_operation_by_id('searchGroup') \
            .Case(query={'q': 'test-search-group-unique'})
        response = case.call(headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(g['name'] == 'test-search-group-unique' for g in data)

    finally:
        delete_group(account_token, group_id)

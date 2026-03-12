from conftest import Secret, free_user_slot, system_admin_account_operations, USERNAME, ADMIN_USERNAME
from schemathesis import Case


def test_listAdminUsers(system_admin_account_token: Secret):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    case: Case = system_admin_account_operations.get_operation_by_id('listAdminUsers').make_case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'admin_user_list' in data
    assert isinstance(data['admin_user_list'], list)
    assert len(data['admin_user_list']) >= 1

    admin_emails = [u['contact_email'] for u in data['admin_user_list']]
    assert ADMIN_USERNAME in admin_emails

    admin = next(u for u in data['admin_user_list'] if u['contact_email'] == ADMIN_USERNAME)
    assert admin['is_staff'] is True
    assert admin['is_active'] is True


def test_searchUser(system_admin_account_token: Secret):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    query = {'query': 'testuser'}
    case: Case = system_admin_account_operations.get_operation_by_id('searchUser') \
        .make_case(query=query)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'user_list' in data
    assert len(data['user_list']) >= 1

    found = [u for u in data['user_list'] if u['contact_email'] == USERNAME]
    assert len(found) == 1
    assert found[0]['is_active'] is True


def test_searchUser_no_results(system_admin_account_token: Secret):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    query = {'query': 'nonexistent-user-xyz-12345'}
    case: Case = system_admin_account_operations.get_operation_by_id('searchUser') \
        .make_case(query=query)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert len(response.json()['user_list']) == 0


def test_resetUserPassword(system_admin_account_token: Secret):
    """Create a temp user, reset their password, then delete them."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # Free a slot and create temp user
    free_user_slot(headers)

    body = {
        'email': 'reset-pw-test@example.com',
        'password': 'OldPassword123!',
        'name': 'Reset PW Test',
    }
    case: Case = system_admin_account_operations.get_operation_by_id('addNewUser') \
        .make_case(body=body)
    response = case.call(headers=headers)
    assert response.status_code == 200
    user_id = response.json()['email']

    try:
        # Reset password
        path_parameters = {'user_id': user_id}
        case: Case = system_admin_account_operations.get_operation_by_id('resetUserPassword') \
            .make_case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert 'new_password' in data
        assert isinstance(data['new_password'], str)
        assert len(data['new_password']) >= 6

    finally:
        case: Case = system_admin_account_operations.get_operation_by_id('deleteUser') \
            .make_case(path_parameters={'user_id': user_id})
        case.call(headers=headers)

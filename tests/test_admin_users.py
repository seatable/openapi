from conftest import Secret, system_admin_account_operations
from schemathesis import Case


def test_admin_user_lifecycle(system_admin_account_token: Secret):
    """Tests addNewUser, updateUser, deleteUser."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    # 1. Create user
    body = {
        'email': 'api-test-user@example.com',
        'password': 'TestPassword123!',
        'name': 'API Test User',
        'is_staff': False,
        'is_active': True,
    }
    case: Case = system_admin_account_operations.find_operation_by_id('addNewUser') \
        .Case(body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    user_id = data['email']  # internal xxx@auth.local format
    assert data['name'] == 'API Test User'
    assert data['contact_email'] == 'api-test-user@example.com'
    assert data['is_active'] is True

    try:
        # 2. Update user
        path_parameters = {'user_id': user_id}
        body = {'name': 'Updated Test User', 'is_active': False}
        case: Case = system_admin_account_operations.find_operation_by_id('updateUser') \
            .Case(path_parameters=path_parameters, body=body)
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert data['name'] == 'Updated Test User'
        assert data['is_active'] is False

    finally:
        # 3. Delete user (always clean up)
        path_parameters = {'user_id': user_id}
        case: Case = system_admin_account_operations.find_operation_by_id('deleteUser') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json()['success'] is True

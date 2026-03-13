import schemathesis
from conftest import (
    BASE_URL, Base, Secret,
    authentication_schema, base_operations_schema, user_account_operations,
    system_admin_account_operations, USERNAME,
)
from schemathesis import Case


# ---------------------------------------------------------------------------
# 1. Login with wrong credentials
# ---------------------------------------------------------------------------

def test_login_wrong_password():
    body = {'username': USERNAME, 'password': 'wrong-password'}
    case: Case = authentication_schema.find_operation_by_id('getAccountTokenfromUsername') \
        .Case(body=body)
    response = case.call()

    assert response.status_code == 400
    assert 'non_field_errors' in response.json()


def test_login_nonexistent_user():
    body = {'username': 'nobody@example.com', 'password': 'irrelevant'}
    case: Case = authentication_schema.find_operation_by_id('getAccountTokenfromUsername') \
        .Case(body=body)
    response = case.call()

    assert response.status_code == 400


def test_login_missing_password():
    body = {'username': USERNAME}
    case: Case = authentication_schema.find_operation_by_id('getAccountTokenfromUsername') \
        .Case(body=body)
    response = case.call()

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# 2. Invalid / missing tokens
# ---------------------------------------------------------------------------

def test_account_endpoint_without_token():
    """Access an account endpoint without Authorization header."""
    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers={})

    assert response.status_code == 403


def test_account_endpoint_with_invalid_token():
    """Access an account endpoint with a garbage token."""
    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers={'Authorization': 'Bearer invalid-token-12345'})

    assert response.status_code == 401


def test_admin_endpoint_as_regular_user(account_token: Secret):
    """Regular user trying to access system admin endpoint."""
    headers = {'Authorization': f'Bearer {account_token.value}'}
    case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
    response = case.call(headers=headers)

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 3. Base token errors
# ---------------------------------------------------------------------------

def test_base_token_for_nonexistent_base(account_token: Secret):
    """Request a base token for a base that doesn't exist."""
    path_parameters = {'workspace_id': 99999, 'base_name': 'nonexistent'}
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithAccountToken') \
        .Case(path_parameters=path_parameters)
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 404


def test_base_token_with_invalid_api_token():
    """Request a base token with an invalid API token."""
    case: Case = authentication_schema.find_operation_by_id('getBaseTokenWithApiToken').Case()
    response = case.call(headers={'Authorization': 'Token invalid-api-token-xyz'})

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# 4. Base operations without / with wrong auth
# ---------------------------------------------------------------------------

def test_base_operation_without_token(base: Base):
    """Access a base operation without any token."""
    path_parameters = {'base_uuid': base.uuid}
    case: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters=path_parameters)
    response = case.call(headers={})

    assert response.status_code == 403


def test_base_operation_with_invalid_token(base: Base):
    """Access a base operation with a garbage base token."""
    path_parameters = {'base_uuid': base.uuid}
    headers = {'Authorization': 'Bearer invalid-jwt-token'}
    case: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters=path_parameters, headers=headers)
    response = case.call()

    assert response.status_code == 403


def test_base_operation_with_wrong_uuid():
    """Access a base that doesn't exist with a valid-looking but wrong UUID."""
    path_parameters = {'base_uuid': '00000000-0000-0000-0000-000000000000'}
    headers = {'Authorization': 'Bearer invalid-jwt-token'}
    case: Case = base_operations_schema.find_operation_by_id('getMetadata') \
        .Case(path_parameters=path_parameters, headers=headers)
    response = case.call()

    assert response.status_code in (401, 403, 404)


# ---------------------------------------------------------------------------
# 5. Row operations on nonexistent resources
# ---------------------------------------------------------------------------

def test_get_nonexistent_row(base: Base):
    """Request a row that doesn't exist."""
    path_parameters = {'base_uuid': base.uuid, 'row_id': 'AAAAAAAAAAAAAAAAAAAAAA'}
    headers = {'Authorization': f'Bearer {base.token}'}
    query = {'table_name': 'Table1'}
    case: Case = base_operations_schema.find_operation_by_id('getRow') \
        .Case(path_parameters=path_parameters, query=query, headers=headers)
    response = case.call()

    assert response.status_code in (400, 404)

from conftest import Base, Secret, authentication_schema
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type


def test_createApiToken(base: Base, account_token: Secret, snapshot_json: SnapshotAssertion):
    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}
    headers = {'Authorization': f'Bearer {account_token.value}'}
    body = {'app_name': 'test-token-create', 'permission': 'rw'}

    case: Case = authentication_schema.get_operation_by_id('createApiToken') \
        .make_case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 201

    data = response.json()
    assert data['app_name'] == 'test-token-create'
    assert data['permission'] == 'rw'
    assert isinstance(data['api_token'], str)
    assert len(data['api_token']) == 40

    matcher = path_type({
        'api_token': (str,),
        'generated_at': (str,),
        'generated_by': (str,),
    })

    assert snapshot_json(matcher=matcher) == data

    # Cleanup
    path_parameters['app_name'] = 'test-token-create'
    case: Case = authentication_schema.get_operation_by_id('deleteApiToken') \
        .make_case(path_parameters=path_parameters)
    case.call(headers=headers)


def test_listApiTokens(base: Base, account_token: Secret, snapshot_json: SnapshotAssertion):
    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # Create a token first
    body = {'app_name': 'test-token-list', 'permission': 'r'}
    case: Case = authentication_schema.get_operation_by_id('createApiToken') \
        .make_case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201

    # List tokens
    case: Case = authentication_schema.get_operation_by_id('listApiTokens') \
        .make_case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'api_tokens' in data
    token_names = [t['app_name'] for t in data['api_tokens']]
    assert 'test-token-list' in token_names

    matcher = path_type({
        r"api_tokens\..*\.api_token": (str,),
        r"api_tokens\..*\.generated_at": (str,),
        r"api_tokens\..*\.generated_by": (str,),
        r"api_tokens\..*\.last_access": (str, type(None)),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data

    # Cleanup
    path_parameters['app_name'] = 'test-token-list'
    case: Case = authentication_schema.get_operation_by_id('deleteApiToken') \
        .make_case(path_parameters=path_parameters)
    case.call(headers=headers)


def test_updateApiToken(base: Base, account_token: Secret):
    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # Create a token
    body = {'app_name': 'test-token-update', 'permission': 'r'}
    case: Case = authentication_schema.get_operation_by_id('createApiToken') \
        .make_case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201
    assert response.json()['permission'] == 'r'

    # Update permission
    path_parameters_with_name = {**path_parameters, 'app_name': 'test-token-update'}
    body = {'permission': 'rw'}
    case: Case = authentication_schema.get_operation_by_id('updateApiToken') \
        .make_case(path_parameters=path_parameters_with_name, body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['permission'] == 'rw'

    # Cleanup
    case: Case = authentication_schema.get_operation_by_id('deleteApiToken') \
        .make_case(path_parameters=path_parameters_with_name)
    case.call(headers=headers)


def test_deleteApiToken(base: Base, account_token: Secret):
    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # Create a token
    body = {'app_name': 'test-token-delete', 'permission': 'r'}
    case: Case = authentication_schema.get_operation_by_id('createApiToken') \
        .make_case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201

    # Delete it
    path_parameters['app_name'] = 'test-token-delete'
    case: Case = authentication_schema.get_operation_by_id('deleteApiToken') \
        .make_case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] is True

import pytest
from conftest import Base, Secret, user_account_operations, create_group, delete_group
from schemathesis import Case


BASE_NAME = 'Automated Tests'


def _headers(account_token: Secret) -> dict:
    return {'Authorization': f'Bearer {account_token.value}'}


def test_getBaseSize(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('getBaseSize') \
        .Case(path_parameters={'base_uuid': base.uuid})
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'result' in data
    assert isinstance(data['result'], int)


def test_searchBaseOrApps(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('searchBaseOrApps') \
        .Case(query={'query_str': 'Automated', 'query_type': 'base'})
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'results' in data
    assert any(BASE_NAME in r['name'] for r in data['results'])


def test_updateBase(base: Base, account_token: Secret):
    """Rename base and rename back."""
    path_parameters = {'workspace_id': base.workspace_id}

    # Rename
    case: Case = user_account_operations.find_operation_by_id('updateBase') \
        .Case(
            path_parameters=path_parameters,
            body={'name': BASE_NAME, 'new_name': 'Automated Tests Renamed'},
        )
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    assert response.json()['table']['name'] == 'Automated Tests Renamed'

    # Rename back so other tests still work
    case: Case = user_account_operations.find_operation_by_id('updateBase') \
        .Case(
            path_parameters=path_parameters,
            body={'name': 'Automated Tests Renamed', 'new_name': BASE_NAME},
        )
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    assert response.json()['table']['name'] == BASE_NAME


def test_folder_lifecycle(base: Base, account_token: Secret):
    """Tests createFolder, deleteFolder."""
    headers = _headers(account_token)
    path_parameters = {'workspace_id': base.workspace_id}

    # Create folder
    case: Case = user_account_operations.find_operation_by_id('createFolder') \
        .Case(
            path_parameters=path_parameters,
            body={'name': 'Test Folder'},
        )
    response = case.call(headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert 'folder' in data
    folder_id = data['folder']['id']

    # Delete folder
    case: Case = user_account_operations.find_operation_by_id('deleteFolder') \
        .Case(
            path_parameters={**path_parameters, 'folder_id': folder_id},
        )
    response = case.call(headers=headers)

    assert response.status_code == 200


def test_listSnapshots(base: Base, account_token: Secret):
    case: Case = user_account_operations.find_operation_by_id('listSnapshots') \
        .Case(
            path_parameters={'workspace_id': base.workspace_id, 'base_name': BASE_NAME},
            query={'page': 1, 'per_page': 25},
        )
    response = case.call(headers=_headers(account_token))

    assert response.status_code == 200
    data = response.json()
    assert 'snapshot_list' in data
    assert isinstance(data['snapshot_list'], list)

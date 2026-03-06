from conftest import (
    Base, Secret, system_admin_account_operations, USERNAME,
    user_account_operations, create_group, delete_group,
)
from schemathesis import Case


def test_listAllBases(system_admin_account_token: Secret, base: Base):
    """List all bases in the system, verify our test base appears."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    case: Case = system_admin_account_operations.get_operation_by_id('listAllBases') \
        .make_case(query={'page': 1, 'per_page': 25})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'dtables' in data
    assert isinstance(data['dtables'], list)

    uuids = [b['uuid'] for b in data['dtables']]
    assert base.uuid in uuids


def test_listUsersBases(system_admin_account_token: Secret, account_token: Secret):
    """Create a base in the user's personal workspace and verify it appears in listUsersBases."""
    admin_headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    user_headers = {'Authorization': f'Bearer {account_token.value}'}

    # Find testuser's internal user_id and personal workspace_id
    case: Case = system_admin_account_operations.get_operation_by_id('listUsers').make_case()
    response = case.call(headers=admin_headers)
    user = next(u for u in response.json()['data'] if u['contact_email'] == USERNAME)
    user_id = user['email']

    case: Case = user_account_operations.get_operation_by_id('listWorkspaces').make_case()
    response = case.call(headers=user_headers)
    personal_ws = next(w for w in response.json()['workspace_list'] if w.get('type') == 'personal')
    ws_id = personal_ws['id']

    # Create a base in the personal workspace
    body = {'workspace_id': ws_id, 'name': 'UserBasesTest'}
    case: Case = user_account_operations.get_operation_by_id('createBase').make_case(body=body)
    response = case.call(headers=user_headers)
    assert response.status_code == 201
    base_uuid = response.json()['table']['uuid']

    try:
        path_parameters = {'user_id': user_id}
        case: Case = system_admin_account_operations.get_operation_by_id('listUsersBases') \
            .make_case(path_parameters=path_parameters)
        response = case.call(headers=admin_headers)

        assert response.status_code == 200

        data = response.json()
        assert 'dtable_list' in data
        assert isinstance(data['dtable_list'], list)
        assert len(data['dtable_list']) >= 1

        uuids = [b['uuid'] for b in data['dtable_list']]
        assert base_uuid in uuids

    finally:
        path_parameters = {'workspace_id': ws_id}
        body = {'name': 'UserBasesTest'}
        case: Case = user_account_operations.get_operation_by_id('deleteBase') \
            .make_case(path_parameters=path_parameters, body=body)
        case.call(headers=user_headers)


def test_listTrashedBases(system_admin_account_token: Secret):
    """List trashed bases (may be empty, just verify the endpoint works)."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    case: Case = system_admin_account_operations.get_operation_by_id('listTrashedBases') \
        .make_case(query={'page': 1, 'per_page': 25})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert 'trash_dtable_list' in data
    assert isinstance(data['trash_dtable_list'], list)


def test_trash_and_restore_base(system_admin_account_token: Secret, account_token: Secret):
    """Delete a base (moves to trash), verify it appears in trash, then restore it."""
    admin_headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    user_headers = {'Authorization': f'Bearer {account_token.value}'}

    # Create a group + base to trash
    group_id, ws_id = create_group(account_token, 'trash-restore-test')

    try:
        body = {'workspace_id': ws_id, 'name': 'TrashMe'}
        case: Case = user_account_operations.get_operation_by_id('createBase').make_case(body=body)
        response = case.call(headers=user_headers)
        assert response.status_code == 201
        base_uuid = response.json()['table']['uuid']
        base_id = response.json()['table']['id']

        # Delete base via admin API (moves to trash)
        case: Case = system_admin_account_operations.get_operation_by_id('deleteBase') \
            .make_case(path_parameters={'base_uuid': base_uuid})
        response = case.call(headers=admin_headers)
        assert response.status_code == 200

        # Verify it appears in trash
        case: Case = system_admin_account_operations.get_operation_by_id('listTrashedBases') \
            .make_case(query={'page': 1, 'per_page': 100})
        response = case.call(headers=admin_headers)
        assert response.status_code == 200

        trashed_ids = [b['id'] for b in response.json()['trash_dtable_list']]
        assert base_id in trashed_ids

        # Restore from trash
        case: Case = system_admin_account_operations.get_operation_by_id('restoreTrashedBase') \
            .make_case(path_parameters={'base_id': base_id})
        response = case.call(headers=admin_headers)
        assert response.status_code == 200

        # Verify it's no longer in trash
        case: Case = system_admin_account_operations.get_operation_by_id('listTrashedBases') \
            .make_case(query={'page': 1, 'per_page': 100})
        response = case.call(headers=admin_headers)
        trashed_ids = [b['id'] for b in response.json()['trash_dtable_list']]
        assert base_id not in trashed_ids

        # Clean up: delete the restored base properly
        path_parameters = {'workspace_id': ws_id}
        body = {'name': 'TrashMe'}
        case: Case = user_account_operations.get_operation_by_id('deleteBase') \
            .make_case(path_parameters=path_parameters, body=body)
        case.call(headers=user_headers)

    finally:
        delete_group(account_token, group_id)

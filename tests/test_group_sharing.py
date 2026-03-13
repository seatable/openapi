from conftest import (
    Base, Secret, user_account_operations,
    create_group, delete_group,
)
from schemathesis import Case


def test_group_share_lifecycle(base: Base, account_token: Secret):
    """Tests createGroupShare, listGroupShares, updateGroupShare, deleteGroupShare."""
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # Create a different group to share the base with (can't share to the owning group)
    group_name = 'share-target-group'
    target_group_id, _ = create_group(account_token, group_name)

    path_parameters = {'workspace_id': base.workspace_id, 'base_name': 'Automated Tests'}

    try:
        # 1. Create group share (read-only)
        body = {'group_id': str(target_group_id), 'permission': 'r'}
        case: Case = user_account_operations.find_operation_by_id('createGroupShare') \
            .Case(path_parameters=path_parameters, body=body)
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert 'dtable_group_share' in data
        assert int(data['dtable_group_share']['group_id']) == target_group_id
        assert data['dtable_group_share']['permission'] == 'r'

        # 2. List group shares
        case: Case = user_account_operations.find_operation_by_id('listGroupShares') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert 'dtable_group_share_list' in data
        group_ids = [s['group_id'] for s in data['dtable_group_share_list']]
        assert target_group_id in group_ids

        # 3. Update group share (change to read-write)
        path_params_with_group = {**path_parameters, 'group_id': target_group_id}
        body = {'permission': 'rw'}
        case: Case = user_account_operations.find_operation_by_id('updateGroupShare') \
            .Case(path_parameters=path_params_with_group, body=body)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json()['success'] is True

        # 4. Delete group share
        case: Case = user_account_operations.find_operation_by_id('deleteGroupShare') \
            .Case(path_parameters=path_params_with_group)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json()['success'] is True

        # Verify it's gone
        case: Case = user_account_operations.find_operation_by_id('listGroupShares') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        group_ids = [s['group_id'] for s in response.json()['dtable_group_share_list']]
        assert target_group_id not in group_ids

    finally:
        delete_group(account_token, target_group_id)

import pytest
from conftest import TeamAdmin, team_admin_account_operations
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props
from syrupy.matchers import path_type


@pytest.mark.needs_large_license
def test_getTeamInfo(team: TeamAdmin, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {team.account_token}'}

    case: Case = team_admin_account_operations.find_operation_by_id('getTeamInfo').Case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['org_id'] == team.team_id

    matcher = path_type({
        'org_id': (int,),
        'org_name': (str,),
        'member_usage': (int,),
        'member_quota': (int,),
        'active_members': (int,),
        'role': (str,),
        'storage_quota': (int,),
        'storage_usage': (int,),
        'row_usage': (int,),
        'row_total': (int,),
        'big_data_row_limit': (int,),
        'big_data_storage_quota': (int,),
        'big_data_total_rows': (int,),
        'big_data_total_storage': (int,),
        'api_calls_count': (int,),
        'api_calls_limit': (int,),
        'automation_count': (int,),
        'automation_limit': (int,),
        'scripts_running_count': (int,),
    })

    assert snapshot_json(matcher=matcher) == data


@pytest.mark.needs_large_license
def test_listGroups(team: TeamAdmin, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {team.account_token}'}
    path_parameters = {'org_id': team.team_id}

    # Get the admin's internal @auth.local user ID
    case: Case = team_admin_account_operations.find_operation_by_id('listTeamUsers').Case(
        path_parameters=path_parameters,
    )
    response = case.call(headers=headers)
    assert response.status_code == 200
    admin_user_id = response.json()['user_list'][0]['email']

    # Create a group so the list is non-empty
    case: Case = team_admin_account_operations.find_operation_by_id('addGroup').Case(
        path_parameters=path_parameters,
        body={'group_name': 'Test Group', 'group_owner': admin_user_id},
    )
    response = case.call(headers=headers)
    assert response.status_code == 200

    # List groups
    case: Case = team_admin_account_operations.find_operation_by_id('listGroups').Case(
        path_parameters=path_parameters,
    )
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data['groups'], list)
    assert len(data['groups']) == 1
    assert data['page'] == 1
    assert isinstance(data['per_page'], int)
    assert isinstance(data['page_next'], bool)

    group = data['groups'][0]
    assert group['group_name'] == 'Test Group'

    matcher = path_type({
        'id': (int,),
        'ctime': (str,),
        'creator_name': (str,),
        'creator_email': (str,),
        'size': (int,),
    })

    assert snapshot_json(matcher=matcher) == group


@pytest.mark.needs_large_license
def test_listGroupMembers(team: TeamAdmin, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {team.account_token}'}
    path_parameters = {'org_id': team.team_id}

    # Get the admin's internal @auth.local user ID
    case: Case = team_admin_account_operations.find_operation_by_id('listTeamUsers').Case(
        path_parameters=path_parameters,
    )
    response = case.call(headers=headers)
    assert response.status_code == 200
    admin_user_id = response.json()['user_list'][0]['email']

    # Create a group
    case: Case = team_admin_account_operations.find_operation_by_id('addGroup').Case(
        path_parameters=path_parameters,
        body={'group_name': 'Members Test Group', 'group_owner': admin_user_id},
    )
    response = case.call(headers=headers)
    assert response.status_code == 200
    group_id = response.json()['id']

    # List group members
    case: Case = team_admin_account_operations.find_operation_by_id('listGroupMembers').Case(
        path_parameters={**path_parameters, 'group_id': group_id},
    )
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['group_id'] == group_id
    assert data['group_name'] == 'Members Test Group'
    assert isinstance(data['members'], list)
    assert len(data['members']) == 1

    member = data['members'][0]
    assert member['email'] == admin_user_id
    assert member['role'] == 'Owner'

    matcher = path_type({
        'group_id': (int,),
        'email': (str,),
        'name': (str,),
        'contact_email': (str,),
        'avatar_url': (str,),
    })

    assert snapshot_json(matcher=matcher) == member

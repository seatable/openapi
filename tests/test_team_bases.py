import pytest
from conftest import (
    TeamAdmin, team_admin_account_operations, user_account_operations, generate_password,
)
from random import randint
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

pytestmark = pytest.mark.needs_large_license


def test_listBasesSharedToUser(team: TeamAdmin, snapshot_json: SnapshotAssertion):
    """Share a base from the team admin to a team member and verify it appears in listBasesSharedToUser."""
    headers = {'Authorization': f'Bearer {team.account_token}'}
    path_parameters = {'org_id': team.team_id}

    # Add a user to the team (emails are reserved forever, so use a unique one per run)
    body = {
        'email': f'shared-bases-test-{randint(1, 1000000)}@example.com',
        'name': 'Shared Bases Test',
        'password': generate_password(),
        'with_workspace': True,
    }
    case: Case = team_admin_account_operations.find_operation_by_id('addUser') \
        .Case(path_parameters=path_parameters, body=body)
    response = case.call(headers=headers)
    assert response.status_code == 200
    user_id = response.json()['email']

    # Get the team admin's own user ID and personal workspace
    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    admin_user_id = response.json()['email']

    case: Case = user_account_operations.find_operation_by_id('listWorkspaces').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    ws_id = next(w for w in response.json()['workspace_list'] if w.get('type') == 'personal')['id']

    body = {'workspace_id': ws_id, 'name': 'SharedBasesTest'}
    case: Case = user_account_operations.find_operation_by_id('createBase').Case(body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201
    base_uuid = response.json()['table']['uuid']

    # Share the base to the new user
    body = {'email': user_id, 'permission': 'r'}
    case: Case = user_account_operations.find_operation_by_id('createUserShare') \
        .Case(path_parameters={'workspace_id': ws_id, 'base_name': 'SharedBasesTest'}, body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201

    # List bases shared to the user
    case: Case = team_admin_account_operations.find_operation_by_id('listBasesSharedToUser') \
        .Case(path_parameters={'org_id': team.team_id, 'user_id': user_id})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 1
    assert len(data['dtable_list']) == 1

    shared_base = data['dtable_list'][0]
    assert shared_base['uuid'] == base_uuid
    assert shared_base['from_user'] == admin_user_id

    matcher = path_type({
        r"dtable_list\.\d+\.id": (int,),
        r"dtable_list\.\d+\.workspace_id": (int,),
        r"dtable_list\.\d+\.uuid": (str,),
        r"dtable_list\.\d+\.created_at": (str,),
        r"dtable_list\.\d+\.updated_at": (str,),
        r"dtable_list\.\d+\.creator": (str,),
        r"dtable_list\.\d+\.modifier": (str,),
        r"dtable_list\.\d+\.file_size": (int,),
        r"dtable_list\.\d+\.from_user": (str,),
        r"dtable_list\.\d+\.from_user_name": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


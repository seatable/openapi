import json
import pytest
import requests
from conftest import (
    BASE_URL, Secret, TeamAdmin, system_admin_account_operations, team_admin_account_operations,
    user_account_operations,
)
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

pytestmark = pytest.mark.needs_large_license


def test_listManagedApps(team: TeamAdmin, system_admin_account_token: Secret, snapshot_json: SnapshotAssertion):
    """Create a universal app, make the team admin its admin and verify it appears in listManagedApps."""
    headers = {'Authorization': f'Bearer {team.account_token}'}
    path_parameters = {'org_id': team.team_id}

    # Custom app roles require the "advanced customization" permission, which the default team role lacks
    case: Case = system_admin_account_operations.find_operation_by_id('updateTeam') \
        .Case(path_parameters=path_parameters, body={'role': 'org_enterprise'})
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
    assert response.status_code == 200

    # The team admin will be the app's admin, so get their own user ID
    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    user_id = response.json()['email']

    # Create a base in the team admin's personal workspace
    case: Case = user_account_operations.find_operation_by_id('listWorkspaces').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    ws_id = next(w for w in response.json()['workspace_list'] if w.get('type') == 'personal')['id']

    body = {'workspace_id': ws_id, 'name': 'ManagedAppsTest'}
    case: Case = user_account_operations.find_operation_by_id('createBase').Case(body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201
    base_uuid = response.json()['table']['uuid']

    # Create a universal app, an "admin" role and add the team admin with that role (endpoints not in the spec)
    app_config = json.dumps({'app_type': 'universal-app', 'app_name': 'Test App', 'settings': {'pages': [], 'navigation': []}})
    response = requests.post(
        f'{BASE_URL}/api/v2.1/workspace/{ws_id}/dtable/ManagedAppsTest/external-apps/',
        headers=headers, data={'app_type': 'universal-app', 'app_config': app_config},
    )
    assert response.status_code == 201
    app_uuid = response.json()['external_app']['app_uuid']

    response = requests.post(
        f'{BASE_URL}/api/v2.1/universal-apps/{app_uuid}/app-roles/',
        headers=headers, data={'role_name': 'admin', 'permission': 'rw'},
    )
    assert response.status_code == 200
    role_id = response.json()['app_role']['id']

    response = requests.post(
        f'{BASE_URL}/api/v2.1/universal-apps/{app_uuid}/app-users/',
        headers=headers, data={'app_user': user_id, 'app_role_id': role_id},
    )
    assert response.status_code == 200

    # List the user's managed apps
    case: Case = team_admin_account_operations.find_operation_by_id('listManagedApps') \
        .Case(path_parameters={'org_id': team.team_id, 'user_id': user_id})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 1
    assert len(data['managed_apps']) == 1

    managed_app = data['managed_apps'][0]
    assert managed_app['app_uuid'] == app_uuid
    assert managed_app['dtable_uuid'] == base_uuid.replace('-', '')

    matcher = path_type({
        r"managed_apps\.\d+\.app_user_id": (int,),
        r"managed_apps\.\d+\.app_id": (int,),
        r"managed_apps\.\d+\.app_uuid": (str,),
        r"managed_apps\.\d+\.dtable_uuid": (str,),
        r"managed_apps\.\d+\.workspace_id": (int,),
        r"managed_apps\.\d+\.link": (str,),
        r"managed_apps\.\d+\.edit_link": (str,),
        r"managed_apps\.\d+\.joined_at": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data


def test_listUsableApps(team: TeamAdmin, snapshot_json: SnapshotAssertion):
    """Create a universal app, add the team admin with the default role and verify it appears in listUsableApps."""
    headers = {'Authorization': f'Bearer {team.account_token}'}

    case: Case = user_account_operations.find_operation_by_id('getAccountInfo').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    user_id = response.json()['email']

    # Create a base in the team admin's personal workspace
    case: Case = user_account_operations.find_operation_by_id('listWorkspaces').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    ws_id = next(w for w in response.json()['workspace_list'] if w.get('type') == 'personal')['id']

    body = {'workspace_id': ws_id, 'name': 'UsableAppsTest'}
    case: Case = user_account_operations.find_operation_by_id('createBase').Case(body=body)
    response = case.call(headers=headers)
    assert response.status_code == 201
    base_uuid = response.json()['table']['uuid']

    # Create a universal app and add the team admin with its auto-created "default" role (endpoints not in the spec)
    app_config = json.dumps({'app_type': 'universal-app', 'app_name': 'Test App', 'settings': {'pages': [], 'navigation': []}})
    response = requests.post(
        f'{BASE_URL}/api/v2.1/workspace/{ws_id}/dtable/UsableAppsTest/external-apps/',
        headers=headers, data={'app_type': 'universal-app', 'app_config': app_config},
    )
    assert response.status_code == 201
    app_uuid = response.json()['external_app']['app_uuid']

    response = requests.get(f'{BASE_URL}/api/v2.1/universal-apps/{app_uuid}/app-roles/', headers=headers)
    assert response.status_code == 200
    role_id = next(r['id'] for r in response.json()['app_roles'] if r['role_name'] == 'default')

    response = requests.post(
        f'{BASE_URL}/api/v2.1/universal-apps/{app_uuid}/app-users/',
        headers=headers, data={'app_user': user_id, 'app_role_id': role_id},
    )
    assert response.status_code == 200

    # List the apps the user can use
    case: Case = team_admin_account_operations.find_operation_by_id('listUsableApps') \
        .Case(path_parameters={'org_id': team.team_id, 'user_id': user_id})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['count'] == 1
    assert len(data['can_use_apps']) == 1

    usable_app = data['can_use_apps'][0]
    assert usable_app['app_uuid'] == app_uuid
    assert usable_app['dtable_uuid'] == base_uuid.replace('-', '')

    matcher = path_type({
        r"can_use_apps\.\d+\.app_user_id": (int,),
        r"can_use_apps\.\d+\.app_id": (int,),
        r"can_use_apps\.\d+\.app_uuid": (str,),
        r"can_use_apps\.\d+\.dtable_uuid": (str,),
        r"can_use_apps\.\d+\.workspace_id": (int,),
        r"can_use_apps\.\d+\.link": (str,),
        r"can_use_apps\.\d+\.edit_link": (str,),
        r"can_use_apps\.\d+\.joined_at": (str,),
    }, regex=True)

    assert snapshot_json(matcher=matcher) == data

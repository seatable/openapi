import pytest
from conftest import TeamAdmin, team_admin_account_operations
from schemathesis import Case


@pytest.mark.needs_large_license
def test_getTeamSettings(team: TeamAdmin):
    headers = {'Authorization': f'Bearer {team.account_token}'}

    case: Case = team_admin_account_operations.find_operation_by_id('getTeamSettings').Case()
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data['enable_force_2fa'], bool)
    assert isinstance(data['enable_force_sso_login'], bool)
    assert isinstance(data['enable_new_user_email'], bool)
    assert isinstance(data['enable_external_user_access_invite_link'], bool)
    assert isinstance(data['enable_member_modify_name'], bool)


@pytest.mark.needs_large_license
def test_updateTeamSettings(team: TeamAdmin):
    headers = {'Authorization': f'Bearer {team.account_token}'}

    # Fetch current settings to toggle a known value
    case: Case = team_admin_account_operations.find_operation_by_id('getTeamSettings').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    original = response.json()

    new_value = not original['enable_force_2fa']
    body = {'enable_force_2fa': new_value}

    case: Case = team_admin_account_operations.find_operation_by_id('updateTeamSettings').Case(body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['enable_force_2fa'] == new_value

    # Verify the change is persisted
    case: Case = team_admin_account_operations.find_operation_by_id('getTeamSettings').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    assert response.json()['enable_force_2fa'] == new_value

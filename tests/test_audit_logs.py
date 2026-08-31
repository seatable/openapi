import pytest
from conftest import (
    CLEANUP_AFTER_TESTS,
    TeamAdmin,
    authentication_schema,
    generate_password,
    system_admin_account_operations,
    team_admin_account_operations,
    user_account_operations,
)
from random import randint
from schemathesis import Case


def _headers(team: TeamAdmin) -> dict:
    return {'Authorization': f'Bearer {team.account_token}'}


def _team_admin_call(team: TeamAdmin, operation_id: str, **kwargs):
    """Call a team-admin operation as the org admin."""
    case: Case = team_admin_account_operations.find_operation_by_id(operation_id).Case(**kwargs)
    return case.call(headers=_headers(team))


def _user_call(team: TeamAdmin, operation_id: str, **kwargs):
    """Call a user-level operation as the team admin.

    The org audit log only records operations performed through the user-level
    endpoints; team-admin endpoints are not audited at all.
    """
    case: Case = user_account_operations.find_operation_by_id(operation_id).Case(**kwargs)
    return case.call(headers=_headers(team))


def _audit_log_operations(team: TeamAdmin) -> list[str]:
    """Return the `operation` value of every audit log entry stored for the org."""
    response = _team_admin_call(
        team, 'listAuditLogs',
        path_parameters={'org_id': team.team_id},
        query={'page': 1, 'per_page': 100},
    )
    assert response.status_code == 200
    return [e['operation'] for e in response.json()['audit_log_list']]


def _assert_audited(team: TeamAdmin, operation: str):
    assert operation in _audit_log_operations(team), \
        f'operation {operation!r} was not stored in the audit log'


def _unique(prefix: str) -> str:
    # Group/base names may only contain letters, numbers, blank, hyphen, dot, quote or
    # underscore — a numeric suffix keeps them unique within the shared org.
    return f'{prefix} {randint(1, 1_000_000)}'


def _new_group(team: TeamAdmin, name: str) -> tuple[int, int]:
    """Create a group (the caller becomes owner); return (group_id, workspace_id)."""
    response = _user_call(team, 'createGroup', body={'name': name})
    assert response.status_code in (200, 201), f'createGroup failed: {response.status_code} {response.text}'
    groups = _user_call(team, 'listGroups').json()
    group_id = next(g['id'] for g in groups if g['name'] == name)
    workspaces = _user_call(team, 'listWorkspaces').json()['workspace_list']
    workspace_id = next(w['id'] for w in workspaces if w['type'] == 'group' and w['name'] == name)
    return group_id, workspace_id


def _new_base(team: TeamAdmin, name: str, workspace_id: int | None = None) -> tuple[int, str]:
    """Create a base (personal, or in a group workspace); return (workspace_id, uuid)."""
    body = {'name': name}
    if workspace_id is not None:
        body['workspace_id'] = workspace_id
    table = _user_call(team, 'createBase', body=body).json()['table']
    return table['workspace_id'], table['uuid']


def _add_user(team: TeamAdmin, label: str) -> str:
    """Add a throwaway org member; return its user id. Emails are unique per call because
    SeaTable reserves them permanently at the ccnet layer once used."""
    response = _team_admin_call(team, 'addUser', path_parameters={'org_id': team.team_id}, body={
        'email': f'audit-{label}-{randint(1, 1_000_000)}@example.com',
        'name': label,
        'password': generate_password(),
    })
    assert response.status_code == 200, f'addUser failed: {response.status_code} {response.text}'
    return response.json()['email']


@pytest.fixture(scope='module')
def audit_team(system_admin_account_token) -> TeamAdmin:
    """A dedicated org shared by every test in this module (built once).

    The conftest `team` fixture is function-scoped; a module-scoped org keeps the
    audit-log tests from each paying the org-creation cost.
    """
    sys_headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    # Admin emails are reserved at the ccnet layer once used, so make it unique per run.
    admin_email = f'automated-testing-audit-admin-{randint(1, 1_000_000)}@seatable.io'
    admin_password = generate_password()

    response = system_admin_account_operations.find_operation_by_id('addTeam').Case(body={
        'org_name': f'automated-testing-audit-org-{randint(1, 10000)}',
        'admin_email': admin_email,
        'password': admin_password,
        'with_workspace': True,
    }).call(headers=sys_headers)
    assert response.status_code == 200
    team_id = response.json()['org_id']

    response = authentication_schema.find_operation_by_id('getAccountTokenfromUsername').Case(
        body={'username': admin_email, 'password': admin_password},
    ).call()
    assert response.status_code == 200

    yield TeamAdmin(team_id=team_id, account_token=response.json()['token'])

    if CLEANUP_AFTER_TESTS == 'True':
        system_admin_account_operations.find_operation_by_id('deleteTeam').Case(
            path_parameters={'org_id': team_id},
        ).call(headers=sys_headers)


@pytest.mark.needs_large_license
def test_listAuditLogs(team: TeamAdmin):
    response = _team_admin_call(
        team, 'listAuditLogs',
        path_parameters={'org_id': team.team_id},
        query={'page': 1, 'per_page': 25},
    )

    assert response.status_code == 200
    data = response.json()
    assert 'count' in data


# Reasons for the xfail markers below: the org audit log does not record personal-workspace
# base lifecycle, and account deletion is only reachable via the never-audited team-admin
# endpoint. Those actions still run; we expect them to be absent from the log.
_NOT_AUDITED_BASE = 'org audit log does not record personal-workspace base lifecycle'
_NOT_AUDITED_ACCOUNT = 'account deletion is only reachable via the never-audited team-admin endpoint'


@pytest.mark.needs_large_license
def test_group_create_is_audited(audit_team: TeamAdmin):
    _new_group(audit_team, _unique('Audit Group'))
    _assert_audited(audit_team, 'group_create')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason='team-admin endpoints are not captured in the audit log', strict=True)
def test_addGroup_is_audited(team: TeamAdmin):
    """Creating a group via the team-admin `addGroup` should be audited, but isn't:
    team-admin endpoints write nothing to the audit log (only the user-level `createGroup`
    is captured). Uses a fresh org so no user-level group_create entry masks the result."""
    admin_id = _team_admin_call(team, 'listTeamUsers',
                           path_parameters={'org_id': team.team_id}).json()['user_list'][0]['email']
    _team_admin_call(team, 'addGroup', path_parameters={'org_id': team.team_id},
                body={'group_name': _unique('Audit Group'), 'group_owner': admin_id})
    _assert_audited(team, 'group_create')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason='team-admin endpoints are not captured in the audit log', strict=True)
def test_updateGroup_rename_is_audited(team: TeamAdmin):
    """Renaming a group via the team-admin `updateGroup` should be audited, but isn't:
    team-admin endpoints write nothing to the audit log (only the user-level `updateGroup`
    is captured). Uses a fresh org so no user-level group_rename entry masks the result."""
    name = _unique('Audit Group')
    group_id, _ = _new_group(team, name)
    _team_admin_call(team, 'updateGroup', path_parameters={'org_id': team.team_id, 'group_id': group_id},
                body={'new_group_name': f'{name} Renamed'})
    _assert_audited(team, 'group_rename')


@pytest.mark.needs_large_license
def test_group_rename_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Group')
    group_id, _ = _new_group(audit_team, name)
    _user_call(audit_team, 'updateGroup', path_parameters={'group_id': group_id},
               body={'name': f'{name} Renamed'})
    _assert_audited(audit_team, 'group_rename')


@pytest.mark.needs_large_license
def test_group_base_create_is_audited(audit_team: TeamAdmin):
    _, workspace_id = _new_group(audit_team, _unique('Audit Group'))
    _new_base(audit_team, _unique('Audit Group Base'), workspace_id=workspace_id)
    _assert_audited(audit_team, 'group_base_create')


@pytest.mark.needs_large_license
def test_group_base_rename_is_audited(audit_team: TeamAdmin):
    _, workspace_id = _new_group(audit_team, _unique('Audit Group'))
    base_name = _unique('Audit Group Base')
    _new_base(audit_team, base_name, workspace_id=workspace_id)
    _user_call(audit_team, 'updateBase', path_parameters={'workspace_id': workspace_id},
               body={'name': base_name, 'new_name': f'{base_name} Renamed'})
    _assert_audited(audit_team, 'group_base_rename')


@pytest.mark.needs_large_license
def test_group_base_delete_is_audited(audit_team: TeamAdmin):
    _, workspace_id = _new_group(audit_team, _unique('Audit Group'))
    base_name = _unique('Audit Group Base')
    _new_base(audit_team, base_name, workspace_id=workspace_id)
    _user_call(audit_team, 'deleteBase', path_parameters={'workspace_id': workspace_id},
               body={'name': base_name})
    _assert_audited(audit_team, 'group_base_delete')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason='team-admin endpoints are not captured in the audit log', strict=True)
def test_deleteBase_is_audited(team: TeamAdmin):
    """Deleting a base via the team-admin `deleteBase` should be audited, but isn't:
    team-admin endpoints write nothing to the audit log (only the user-level `deleteBase`
    is captured). Uses a group base in a fresh org so no user-level group_base_delete entry
    masks the result, and so the user-level equivalent really would be audited."""
    _, workspace_id = _new_group(team, _unique('Audit Group'))
    _, uuid = _new_base(team, _unique('Audit Group Base'), workspace_id=workspace_id)
    _team_admin_call(team, 'deleteBase', path_parameters={'org_id': team.team_id, 'base_uuid': uuid})
    _assert_audited(team, 'group_base_delete')


@pytest.mark.needs_large_license
def test_group_base_restore_is_audited(audit_team: TeamAdmin):
    group_id, workspace_id = _new_group(audit_team, _unique('Audit Group'))
    base_name = _unique('Audit Group Base')
    _, uuid = _new_base(audit_team, base_name, workspace_id=workspace_id)
    _user_call(audit_team, 'deleteBase', path_parameters={'workspace_id': workspace_id},
               body={'name': base_name})
    _user_call(audit_team, 'restoreGroupTrashedBase',
               path_parameters={'group_id': group_id, 'base_uuid': uuid})
    _assert_audited(audit_team, 'group_base_restore')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason='team-admin endpoints are not captured in the audit log', strict=True)
def test_restoreBaseFromTrash_is_audited(team: TeamAdmin):
    """Restoring a base via the team-admin `restoreBaseFromTrash` should be audited, but isn't:
    team-admin endpoints write nothing to the audit log (only the user-level
    `restoreGroupTrashedBase` is captured). Uses a group base in a fresh org so no user-level
    group_base_restore entry masks the result, and so the user-level equivalent really would
    be audited. The base is deleted via the user-level endpoint to land it in the trash bin."""
    _, workspace_id = _new_group(team, _unique('Audit Group'))
    base_name = _unique('Audit Group Base')
    _, uuid = _new_base(team, base_name, workspace_id=workspace_id)
    _user_call(team, 'deleteBase', path_parameters={'workspace_id': workspace_id},
               body={'name': base_name})
    _team_admin_call(team, 'restoreBaseFromTrash', path_parameters={'org_id': team.team_id, 'base_uuid': uuid})
    _assert_audited(team, 'group_base_restore')


@pytest.mark.needs_large_license
def test_group_delete_is_audited(audit_team: TeamAdmin):
    group_id, _ = _new_group(audit_team, _unique('Audit Group'))
    _user_call(audit_team, 'deleteGroup', path_parameters={'group_id': group_id})
    _assert_audited(audit_team, 'group_delete')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason='team-admin endpoints are not captured in the audit log', strict=True)
def test_deleteGroup_is_audited(team: TeamAdmin):
    """Deleting a group via the team-admin `deleteGroup` should be audited, but isn't:
    team-admin endpoints write nothing to the audit log (only the user-level `deleteGroup`
    is captured). Uses a fresh org so no user-level group_delete entry masks the result.
    The freshly created group is empty, which `deleteGroup` requires."""
    group_id, _ = _new_group(team, _unique('Audit Group'))
    _team_admin_call(team, 'deleteGroup', path_parameters={'org_id': team.team_id, 'group_id': group_id})
    _assert_audited(team, 'group_delete')


@pytest.mark.needs_large_license
def test_group_transfer_is_audited(audit_team: TeamAdmin):
    group_id, _ = _new_group(audit_team, _unique('Audit Group'))
    target = _add_user(audit_team, 'transfer-target')
    _user_call(audit_team, 'updateGroup', path_parameters={'group_id': group_id},
               body={'owner': target})
    _assert_audited(audit_team, 'group_transfer')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason=_NOT_AUDITED_BASE, strict=True)
def test_base_create_is_audited(audit_team: TeamAdmin):
    _new_base(audit_team, _unique('Audit Base'))
    _assert_audited(audit_team, 'base_create')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason=_NOT_AUDITED_BASE, strict=True)
def test_base_rename_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    _user_call(audit_team, 'updateBase', path_parameters={'workspace_id': workspace_id},
               body={'name': name, 'new_name': f'{name} Renamed'})
    _assert_audited(audit_team, 'base_rename')


@pytest.mark.needs_large_license
def test_base_external_link_create_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    _user_call(audit_team, 'createBaseExternalLink',
               path_parameters={'workspace_id': workspace_id, 'base_name': name},
               body={'expire_days': 7})
    _assert_audited(audit_team, 'base_external_link_create')


@pytest.mark.needs_large_license
def test_base_external_link_delete_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    token = _user_call(audit_team, 'createBaseExternalLink',
                       path_parameters={'workspace_id': workspace_id, 'base_name': name},
                       body={'expire_days': 7}).json()['token']
    _user_call(audit_team, 'deleteExternalLink',
               path_parameters={'workspace_id': workspace_id, 'base_name': name,
                                'external_link_token': token})
    _assert_audited(audit_team, 'base_external_link_delete')


@pytest.mark.needs_large_license
def test_base_invite_link_create_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    _user_call(audit_team, 'createInviteLink',
               body={'table_name': name, 'workspace_id': workspace_id, 'permission': 'rw'})
    _assert_audited(audit_team, 'base_invite_link_create')


@pytest.mark.needs_large_license
def test_base_invite_link_delete_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    token = _user_call(audit_team, 'createInviteLink',
                       body={'table_name': name, 'workspace_id': workspace_id, 'permission': 'rw'}).json()['token']
    _user_call(audit_team, 'deleteInviteLink', path_parameters={'invite_link_token': token})
    _assert_audited(audit_team, 'base_invite_link_delete')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason=_NOT_AUDITED_BASE, strict=True)
def test_base_delete_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    _user_call(audit_team, 'deleteBase', path_parameters={'workspace_id': workspace_id},
               body={'name': name})
    _assert_audited(audit_team, 'base_delete')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason=_NOT_AUDITED_BASE, strict=True)
def test_base_restore_is_audited(audit_team: TeamAdmin):
    name = _unique('Audit Base')
    workspace_id, _ = _new_base(audit_team, name)
    _user_call(audit_team, 'deleteBase', path_parameters={'workspace_id': workspace_id},
               body={'name': name})
    base_id = next(b['id'] for b in _user_call(audit_team, 'listTrashedBases').json()['trash_dtable_list']
                   if b['name'] == name)
    _user_call(audit_team, 'restoreTrashedBase', path_parameters={'trashed_base_id': base_id})
    _assert_audited(audit_team, 'base_restore')


@pytest.mark.needs_large_license
@pytest.mark.xfail(reason=_NOT_AUDITED_ACCOUNT, strict=True)
def test_account_delete_is_audited(audit_team: TeamAdmin):
    user_id = _add_user(audit_team, 'delete-target')
    _team_admin_call(audit_team, 'deleteUser', path_parameters={'org_id': audit_team.team_id, 'user_id': user_id})
    _assert_audited(audit_team, 'account_delete')

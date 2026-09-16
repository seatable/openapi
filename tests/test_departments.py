import pytest
from conftest import (
    Secret, system_admin_account_operations,
    create_department, delete_department, list_departments,
)
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type

pytestmark = pytest.mark.needs_large_license

# IDs are auto-incremented and differ between runs
DEPARTMENT_MATCHER = path_type({
    r'(.*\.)?id': (int,),
    r'(.*\.)?parent_id': (int,),
    r'(.*\.)?id_in_org': (int,),
}, regex=True)

MEMBER_MATCHER = path_type({
    r'(.*\.)?email': (str,),
    r'(.*\.)?avatar_url': (str,),
}, regex=True)


def test_listDepartments_top_level(system_admin_account_token: Secret, top_department: int, snapshot_json: SnapshotAssertion):
    case: Case = system_admin_account_operations.find_operation_by_id('listDepartments').Case()
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200

    data = response.json()
    assert [d['id'] for d in data['department_list']] == [top_department]

    assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data


def test_addDepartment(system_admin_account_token: Secret, top_department: int, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}

    body = {'name': 'Developers', 'parent_id': top_department}
    case: Case = system_admin_account_operations.find_operation_by_id('addDepartment').Case(body=body)
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    department_id = data['department']['id']

    try:
        assert data['department']['name'] == 'Developers'
        assert data['department']['parent_id'] == top_department
        assert data['department']['org_id'] == -1

        assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data

        # Verify the department shows up below its parent
        sub_departments = list_departments(system_admin_account_token, top_department)
        assert [d['id'] for d in sub_departments] == [department_id]

    finally:
        delete_department(system_admin_account_token, department_id)


def test_addDepartment_second_top_level(system_admin_account_token: Secret, top_department: int):
    """Only one top-level department is allowed."""
    body = {'name': 'another-top-level', 'parent_id': -1}
    case: Case = system_admin_account_operations.find_operation_by_id('addDepartment').Case(body=body)
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 400
    assert response.json()['error_msg'] == 'Top department exists'


def test_updateDepartment(system_admin_account_token: Secret, top_department: int, snapshot_json: SnapshotAssertion):
    department_id = create_department(system_admin_account_token, 'old-name', top_department)

    try:
        case: Case = system_admin_account_operations.find_operation_by_id('updateDepartment') \
            .Case(path_parameters={'department_id': department_id}, body={'name': 'new-name'})
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

        assert response.status_code == 200

        data = response.json()
        assert data['department']['id'] == department_id
        assert data['department']['name'] == 'new-name'

        assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data

        sub_departments = list_departments(system_admin_account_token, top_department)
        assert next(d for d in sub_departments if d['id'] == department_id)['name'] == 'new-name'

    finally:
        delete_department(system_admin_account_token, department_id)


def test_deleteDepartment(system_admin_account_token: Secret, top_department: int, snapshot_json: SnapshotAssertion):
    department_id = create_department(system_admin_account_token, 'to-be-deleted', top_department)

    case: Case = system_admin_account_operations.find_operation_by_id('deleteDepartment') \
        .Case(path_parameters={'department_id': department_id})
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})

    assert response.status_code == 200
    assert snapshot_json == response.json()

    sub_departments = list_departments(system_admin_account_token, top_department)
    assert department_id not in [d['id'] for d in sub_departments]


def test_department_members(system_admin_account_token: Secret, top_department: int, user_id: str, snapshot_json: SnapshotAssertion):
    """Add a member, list members, promote the member to department admin, remove the member."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    department_id = create_department(system_admin_account_token, 'members-test', top_department)
    path_parameters = {'department_id': department_id}
    member_path_parameters = {'department_id': department_id, 'user_id': user_id}

    try:
        # Add member
        case: Case = system_admin_account_operations.find_operation_by_id('addDepartmentMembers') \
            .Case(path_parameters=path_parameters, body={'email': [user_id]})
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert data['failed'] == []
        assert [m['email'] for m in data['success']] == [user_id]
        assert snapshot_json(name='add', matcher=MEMBER_MATCHER) == data

        # Adding the same member again fails
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json()['success'] == []
        assert [m['email'] for m in response.json()['failed']] == [user_id]

        # List members
        case = system_admin_account_operations.find_operation_by_id('listDepartmentMembers') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert [m['email'] for m in data['member_list']] == [user_id]
        assert data['member_list'][0]['is_staff'] is False
        assert snapshot_json(name='list', matcher=MEMBER_MATCHER) == data

        # Promote member to department admin
        case = system_admin_account_operations.find_operation_by_id('updateDepartmentMember') \
            .Case(path_parameters=member_path_parameters, body={'is_staff': True})
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert data['member']['email'] == user_id
        assert data['member']['is_staff'] is True
        assert snapshot_json(name='update', matcher=MEMBER_MATCHER) == data

        # Remove member
        case = system_admin_account_operations.find_operation_by_id('removeDepartmentMember') \
            .Case(path_parameters=member_path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert snapshot_json(name='remove') == response.json()

        case = system_admin_account_operations.find_operation_by_id('listDepartmentMembers') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json()['member_list'] == []

    finally:
        delete_department(system_admin_account_token, department_id)


def test_addUserToDepartments(system_admin_account_token: Secret, top_department: int, user_id: str, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    first_id = create_department(system_admin_account_token, 'multi-add-1', top_department)
    second_id = create_department(system_admin_account_token, 'multi-add-2', top_department)

    try:
        # User is already a member of the first department
        case: Case = system_admin_account_operations.find_operation_by_id('addDepartmentMembers') \
            .Case(path_parameters={'department_id': first_id}, body={'email': [user_id]})
        response = case.call(headers=headers)
        assert response.status_code == 200

        body = {'email': user_id, 'department_ids': [first_id, second_id]}
        case = system_admin_account_operations.find_operation_by_id('addUserToDepartments').Case(body=body)
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert [d['id'] for d in data['success']] == [second_id]
        assert [f['department']['id'] for f in data['failed']] == [first_id]
        assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data

    finally:
        delete_department(system_admin_account_token, first_id)
        delete_department(system_admin_account_token, second_id)


def test_department_group(system_admin_account_token: Secret, top_department: int, snapshot_json: SnapshotAssertion):
    """Create the group of a department, fetch it, delete it."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    department_id = create_department(system_admin_account_token, 'group-test', top_department)
    path_parameters = {'department_id': department_id}
    group_matcher = path_type({'group_id': (int,)})

    try:
        # Create group
        case: Case = system_admin_account_operations.find_operation_by_id('createDepartmentGroup') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        group_id = data['group_id']
        assert isinstance(group_id, int)
        assert data['group_name'] == 'group-test'
        assert snapshot_json(name='create', matcher=group_matcher) == data

        # A department can have only one group
        response = case.call(headers=headers)

        assert response.status_code == 400
        assert response.json()['error_msg'] == 'Group of department exists'

        # Get group
        case = system_admin_account_operations.find_operation_by_id('getDepartmentGroup') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json() == {'group_id': group_id, 'group_name': 'group-test'}

        # Renaming the department renames the group
        case = system_admin_account_operations.find_operation_by_id('updateDepartment') \
            .Case(path_parameters=path_parameters, body={'name': 'group-test-renamed'})
        response = case.call(headers=headers)
        assert response.status_code == 200

        case = system_admin_account_operations.find_operation_by_id('getDepartmentGroup') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert response.json() == {'group_id': group_id, 'group_name': 'group-test-renamed'}

        # Delete group
        case = system_admin_account_operations.find_operation_by_id('deleteDepartmentGroup') \
            .Case(path_parameters=path_parameters)
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert snapshot_json(name='delete') == response.json()

    finally:
        delete_department(system_admin_account_token, department_id)


def test_listNonDepartmentUsers(system_admin_account_token: Secret, top_department: int, user_id: str, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    department_id = create_department(system_admin_account_token, 'non-dep-test', top_department)

    try:
        case: Case = system_admin_account_operations.find_operation_by_id('listNonDepartmentUsers').Case()
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert user_id in [u['email'] for u in data['user_list']]

        user = next(u for u in data['user_list'] if u['email'] == user_id)
        assert snapshot_json(matcher=MEMBER_MATCHER) == user

        # Once the user is a department member, they are no longer listed
        case = system_admin_account_operations.find_operation_by_id('addDepartmentMembers') \
            .Case(path_parameters={'department_id': department_id}, body={'email': [user_id]})
        response = case.call(headers=headers)
        assert response.status_code == 200

        case = system_admin_account_operations.find_operation_by_id('listNonDepartmentUsers').Case()
        response = case.call(headers=headers)

        assert response.status_code == 200
        assert user_id not in [u['email'] for u in response.json()['user_list']]

    finally:
        delete_department(system_admin_account_token, department_id)

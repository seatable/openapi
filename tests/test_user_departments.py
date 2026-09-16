import pytest
from conftest import (
    Secret, system_admin_account_operations, user_account_operations, ADMIN_USERNAME,
    create_department, delete_department,
)
from dataclasses import dataclass
from schemathesis import Case
from syrupy.assertion import SnapshotAssertion
from syrupy.matchers import path_type
from typing import Generator

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
    r'(.*\.)?group_id': (int,),
    r'(.*\.)?department_id': (int,),
}, regex=True)


@dataclass
class Department:
    id: int
    group_id: int


@pytest.fixture
def department(system_admin_account_token: Secret, top_department: int, user_id: str) -> Generator[Department, None, None]:
    """A sub-department with a group, of which the regular test user is a department admin."""
    headers = {'Authorization': f'Bearer {system_admin_account_token.value}'}
    department_id = create_department(system_admin_account_token, 'automated-testing-sub', top_department)
    path_parameters = {'department_id': department_id}

    case: Case = system_admin_account_operations.find_operation_by_id('createDepartmentGroup') \
        .Case(path_parameters=path_parameters)
    response = case.call(headers=headers)
    assert response.status_code == 200
    group_id = response.json()['group_id']

    case = system_admin_account_operations.find_operation_by_id('addDepartmentMembers') \
        .Case(path_parameters=path_parameters, body={'email': [user_id]})
    response = case.call(headers=headers)
    assert response.status_code == 200

    case = system_admin_account_operations.find_operation_by_id('updateDepartmentMember') \
        .Case(path_parameters={'department_id': department_id, 'user_id': user_id}, body={'is_staff': True})
    response = case.call(headers=headers)
    assert response.status_code == 200

    yield Department(id=department_id, group_id=group_id)

    delete_department(system_admin_account_token, department_id)


@pytest.fixture(scope='module')
def admin_user_id(system_admin_account_token: Secret) -> str:
    """The internal @auth.local ID of the system admin."""
    case: Case = system_admin_account_operations.find_operation_by_id('listUsers').Case()
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
    assert response.status_code == 200

    user = next(u for u in response.json()['data'] if u['contact_email'] == ADMIN_USERNAME)
    return user['email']


def test_listDepartments(account_token: Secret, top_department: int, department: Department, snapshot_json: SnapshotAssertion):
    case: Case = user_account_operations.find_operation_by_id('listDepartments').Case()
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 200

    data = response.json()
    assert [d['id'] for d in data['departments']] == [top_department, department.id]

    assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data


def test_listUserDepartments(account_token: Secret, department: Department, snapshot_json: SnapshotAssertion):
    case: Case = user_account_operations.find_operation_by_id('listUserDepartments').Case()
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 200

    data = response.json()
    assert [d['id'] for d in data['department_list']] == [department.id]
    assert data['department_list'][0]['sub_departments'] == []

    assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data


def test_listSubDepartments(account_token: Secret, top_department: int, department: Department, snapshot_json: SnapshotAssertion):
    case: Case = user_account_operations.find_operation_by_id('listSubDepartments') \
        .Case(path_parameters={'department_id': top_department})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 200

    data = response.json()
    assert [d['id'] for d in data['department_list']] == [department.id]

    assert snapshot_json(matcher=DEPARTMENT_MATCHER) == data


def test_listDepartmentMembers(account_token: Secret, department: Department, user_id: str, snapshot_json: SnapshotAssertion):
    case: Case = user_account_operations.find_operation_by_id('listDepartmentMembers') \
        .Case(path_parameters={'department_id': department.id})
    response = case.call(headers={'Authorization': f'Bearer {account_token.value}'})

    assert response.status_code == 200

    data = response.json()
    assert [m['email'] for m in data['member_list']] == [user_id]
    assert data['member_list'][0]['is_admin'] is True
    assert data['member_list'][0]['role'] == 'Admin'

    assert snapshot_json(matcher=MEMBER_MATCHER) == data


def test_department_members(account_token: Secret, department: Department, admin_user_id: str, snapshot_json: SnapshotAssertion):
    """As department admin: add a member, promote them to department admin, remove them."""
    headers = {'Authorization': f'Bearer {account_token.value}'}
    path_parameters = {'department_id': department.id}
    member_path_parameters = {'department_id': department.id, 'user_id': admin_user_id}

    # Add member
    case: Case = user_account_operations.find_operation_by_id('addDepartmentMembers') \
        .Case(path_parameters=path_parameters, body={'emails': admin_user_id})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['failed'] == []
    assert [m['email'] for m in data['success']] == [admin_user_id]
    assert data['success'][0]['role'] == 'Member'
    assert snapshot_json(name='add', matcher=MEMBER_MATCHER) == data

    # Adding the same member again fails
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['success'] == []
    assert [m['email'] for m in response.json()['failed']] == [admin_user_id]

    # Promote member to department admin
    case = user_account_operations.find_operation_by_id('updateDepartmentMember') \
        .Case(path_parameters=member_path_parameters, body={'is_admin': 'true'})
    response = case.call(headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data['email'] == admin_user_id
    assert data['is_admin'] is True
    assert data['role'] == 'Admin'
    assert snapshot_json(name='update', matcher=MEMBER_MATCHER) == data

    # Remove member
    case = user_account_operations.find_operation_by_id('removeDepartmentMember') \
        .Case(path_parameters=member_path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert snapshot_json(name='remove') == response.json()

    case = user_account_operations.find_operation_by_id('listDepartmentMembers') \
        .Case(path_parameters=path_parameters)
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert admin_user_id not in [m['email'] for m in response.json()['member_list']]


def test_listDepartmentMemberBases(account_token: Secret, system_admin_account_token: Secret, top_department: int, department: Department, user_id: str, snapshot_json: SnapshotAssertion):
    """Members of an ancestor department can list the personal bases of a department member."""
    headers = {'Authorization': f'Bearer {account_token.value}'}

    # The test user has to be a member of an ancestor department (the top-level department) of `department`
    case: Case = system_admin_account_operations.find_operation_by_id('addDepartmentMembers') \
        .Case(path_parameters={'department_id': top_department}, body={'email': [user_id]})
    response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
    assert response.status_code == 200

    # Create a base in the personal workspace of the test user
    case = user_account_operations.find_operation_by_id('listWorkspaces').Case()
    response = case.call(headers=headers)
    assert response.status_code == 200
    workspace_id = next(w['id'] for w in response.json()['workspace_list'] if w['type'] == 'personal')

    base_name = 'automated-testing-departments'
    case = user_account_operations.find_operation_by_id('createBase') \
        .Case(body={'workspace_id': workspace_id, 'name': base_name})
    response = case.call(headers=headers)
    assert response.status_code == 201
    base_uuid = response.json()['table']['uuid']

    try:
        case = user_account_operations.find_operation_by_id('listDepartmentMemberBases') \
            .Case(path_parameters={'department_id': department.id, 'user_id': user_id})
        response = case.call(headers=headers)

        assert response.status_code == 200

        data = response.json()
        assert [b['uuid'] for b in data['dtable_list']] == [base_uuid]

        matcher = path_type({
            r'dtable_list\..*\.id': (int,),
            r'dtable_list\..*\.workspace_id': (int,),
            r'dtable_list\..*\.uuid': (str,),
            r'dtable_list\..*\.created_at': (str,),
            r'dtable_list\..*\.updated_at': (str,),
        }, regex=True)
        assert snapshot_json(matcher=matcher) == data

    finally:
        case = user_account_operations.find_operation_by_id('deleteBase') \
            .Case(path_parameters={'workspace_id': workspace_id}, body={'name': base_name})
        response = case.call(headers=headers)
        assert response.status_code == 200

        case = system_admin_account_operations.find_operation_by_id('removeDepartmentMember') \
            .Case(path_parameters={'department_id': top_department, 'user_id': user_id})
        response = case.call(headers={'Authorization': f'Bearer {system_admin_account_token.value}'})
        assert response.status_code == 200


def test_getDepartmentGroupMembersCount(account_token: Secret, department: Department, admin_user_id: str, snapshot_json: SnapshotAssertion):
    headers = {'Authorization': f'Bearer {account_token.value}'}

    case: Case = user_account_operations.find_operation_by_id('getDepartmentGroupMembersCount') \
        .Case(path_parameters={'group_id': department.group_id})
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert snapshot_json == response.json()

    # Adding a member increases the count
    case = user_account_operations.find_operation_by_id('addDepartmentMembers') \
        .Case(path_parameters={'department_id': department.id}, body={'emails': admin_user_id})
    response = case.call(headers=headers)
    assert response.status_code == 200

    case = user_account_operations.find_operation_by_id('getDepartmentGroupMembersCount') \
        .Case(path_parameters={'group_id': department.group_id})
    response = case.call(headers=headers)

    assert response.status_code == 200
    assert response.json()['count'] == 2
